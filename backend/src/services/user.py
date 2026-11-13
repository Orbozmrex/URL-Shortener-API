from ..middlewares.security import verify_password, create_token, hash_password
from ..repositories.user import UserRepository
from ..core.exceptions import UserAlreadyExistsError, IncorrectLoginDataError
from ..repositories.user import UserCachedRepository
from ..core.config import CacheSettings
from ..schemas.user import UserResponse
from sqlalchemy.exc import IntegrityError

class UserService:
    def __init__(self, repo: UserRepository, cache: UserCachedRepository):
        self.repo = repo
        self.cache = cache
        self.cache_prefix = CacheSettings.user_prefix
        self.cache_ttl = CacheSettings.user_ttl

    async def get_by_email(self, email):
        cached_user = await self.cache.get(f"{self.cache_prefix}:{email}")
        if cached_user is not None:
            return UserResponse.model_validate(cached_user)

        user = await self.repo.get_by_email(email)

        user_model = UserResponse.model_validate(user)
        await self.cache.set(f"{self.cache_prefix}:{email}", user_model.model_dump(), self.cache_ttl)
        return user_model

    async def register(self, register_data):
        hashed_password = await hash_password(register_data.password)
        try:
            new_user = await self.repo.register(register_data.email, hashed_password)
            token = await create_token({"email": register_data.email})

            user_model = UserResponse.model_validate(new_user)
            await self.cache.set(f"{self.cache_prefix}:{register_data.email}", user_model.model_dump(), self.cache_ttl)
            return {"token": token, "token_type": "Bearer"}
        except IntegrityError:
            await self.repo.session.rollback()
            raise UserAlreadyExistsError("User already exists")

    async def login(self, login_data):
        user = await self.repo.get_by_email(login_data.email)

        verified_password = await verify_password(user, login_data.password)
        if not user or not verified_password:
            raise IncorrectLoginDataError("Incorrect login or password")
        
        token = await create_token({"email": login_data.email})
        return {"token": token, "token_type": "Bearer"}