from ..middlewares.security import verify_password, create_token, hash_password
from ..repositories.user import UserRepository
from ..core.exceptions import UserAlreadyExistsError, IncorrectLoginDataError

class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def get_by_email(self, email):
        user = await self.repo.get_by_email(email)
        return user

    async def register(self, register_data):
        existing_user = await self.repo.get_by_email(register_data.email)
        if existing_user is not None:
            raise UserAlreadyExistsError("User already exists")

        hashed_password = await hash_password(register_data.password)
        await self.repo.register(register_data.email, hashed_password)

        token = await create_token({"email": register_data.email})
        return {"token": token, "token_type": "Bearer"}

    async def login(self, login_data):
        user = await self.repo.get_by_email(login_data.email)

        verified_password = await verify_password(user, login_data.password)
        if not user or not verified_password:
            raise IncorrectLoginDataError("Incorrect login or password")
        
        token = await create_token({"email": login_data.email})
        return {"token": token, "token_type": "Bearer"}