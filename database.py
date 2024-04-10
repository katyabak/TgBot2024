from sqlalchemy import create_engine, Column, String, BigInteger, Text, JSON
from sqlalchemy.orm import declarative_base, sessionmaker
from config import DATABASE_URL

Base = declarative_base()
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()


class UserState(Base):
    __tablename__ = 'user_state'

    user_id = Column(BigInteger, primary_key=True)
    current_command = Column(String(255))
    input_data = Column(Text)
    selected_settings = Column(Text)
    user_info = Column(JSON)


# ф-ция для загрузки состояния пользователя
def load_user_state(user_id):
    return session.query(UserState).filter_by(user_id=user_id).first()


# ф-ция для сохранения состояния пользователя
def save_user_state(user_id, current_command=None, input_data=None, selected_settings=None, user_info=None):
    user_state = session.query(UserState).filter_by(user_id=user_id).first()
    if not user_state:
        user_state = UserState(user_id=user_id)

    if current_command:
        user_state.current_command = current_command
    if input_data:
        user_state.input_data = input_data
    if selected_settings:
        user_state.selected_settings = selected_settings
    if user_info:
        user_state.user_info = user_info

    session.add(user_state)
    session.commit()
