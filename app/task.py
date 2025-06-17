import requests
from app import db
from app.models import StoreStat, User

def fetch_store_stats(user_id):
    user = User.query.get(user_id)
    headers = {'Authorization': f"Bearer {user.ml_access_token}"}
    sales = requests.get(
        f'https://api.mercadolibre.com/orders/search?seller={user.username}',
        headers=headers
    ).json()
    total = sales.get('paging', {}).get('total', 0)
    stat = StoreStat(user_id=user_id, total_sales=total)
    db.session.add(stat)
    db.session.commit()
