# create_initial_master_user.py
from models import Usuario, db, create_db_tables
from sqlalchemy.orm import sessionmaker
from auth.dependencies import get_password_hash # Importa a função de hash

def create_master_user():
    create_db_tables() # Garante que as tabelas existem no banco de dados

    Session = sessionmaker(bind=db)
    session = Session()

    # Verifique se o usuário mestre já existe para evitar duplicatas
    master_email = "master@example.com" # Email do seu usuário mestre
    master_user = session.query(Usuario).filter(Usuario.email == master_email).first()

    if not master_user:
        master_password = "masterpassword123" # ESCOLHA UMA SENHA SEGURA PARA O SEU MESTRE!
        master_password_hashed = get_password_hash(master_password) # Gera o hash da senha

        master_user = Usuario(
            nome="Master Admin",
            email=master_email,
            senha=master_password_hashed,
            ativo=True,
            admin=True # Define este usuário como administrador
        )
        session.add(master_user)
        session.commit()
        print(f"Usuário mestre criado: {master_email} com a senha '{master_password}'.")
        print("Lembre-se de usar esta senha apenas para o primeiro login no app de administração.")
    else:
        print(f"Usuário mestre '{master_email}' já existe no banco de dados.")
    session.close()

if __name__ == "__main__":
    create_master_user()