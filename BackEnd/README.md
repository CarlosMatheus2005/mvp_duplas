# BackEnd - Aluguel de Imóveis

API REST desenvolvida em Django e Django REST Framework para o projeto de aluguel de temporada.

## 🚀 Como rodar o projeto

Clone o repositório e siga os passos abaixo no terminal:

```bash
cd BackEnd

# Criar e ativar o ambiente virtual
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# (Lembre de gerar uma SECRET_KEY e colar no seu .env)

# Rodar migrações e criar o admin
python manage.py migrate
python manage.py createsuperuser

# Iniciar o servidor
python manage.py runserver

O servidor vai rodar em http://127.0.0.1:8000/.

Painel Admin: http://127.0.0.1:8000/admin/

Documentação (Swagger): http://127.0.0.1:8000/api/docs/

🛠️ Endpoints Principais
Usuários: /api/usuarios/registro/, /api/usuarios/login/, /api/usuarios/me/

Imóveis: /api/imoveis/ (suporta filtros por cidade, preço, hóspedes e datas)

Comodidades: /api/comodidades/

Reservas: /api/reservas/ (cálculo automático de valor e validação de datas)

Avaliações: /api/avaliacoes/

📌 Regras de Negócio Implementadas
Autenticação via JWT (SimpleJWT).

Apenas o anfitrião dono do imóvel pode editá-lo ou removê-lo.

O valor total da reserva é calculado automaticamente pelo backend (dias × preço da diária).

Validação para impedir conflito de datas nas reservas e garantir que só avalie quem teve a reserva aprovada.

📂 Estrutura
BackEnd/
├── manage.py
├── requirements.txt
├── setup/      # Configurações globais (settings, urls)
├── usuarios/   # App de autenticação e perfil
└── core/       # App de imóveis, reservas e avaliações