import random
from datetime import datetime, timedelta, date

from sqlalchemy.orm import Session

from app.database import SessionLocal, Base, engine
from app.models.user import User, UserRole
from app.models.record import FinancialRecord, RecordType
from app.utils.security import hash_password

def seed_db():
    print("Recreating database schema...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        print("Creating users...")
        users_data = [
            ("admin@zovryn.org", "Admin User", "adminpass", UserRole.ADMIN),
            ("analyst@zovryn.org", "Analyst User", "analystpass", UserRole.ANALYST),
            ("viewer@zovryn.org", "Viewer User", "viewerpass", UserRole.VIEWER),
        ]
        
        seeded_users = []
        for email, name, pwd, role in users_data:
            u = User(email=email, full_name=name, hashed_password=hash_password(pwd), role=role)
            db.add(u)
            seeded_users.append(u)
        
        db.commit()
        for u in seeded_users:
            db.refresh(u)

        print("Creating financial records...")
        categories_income = ["salary", "bonus", "freelance", "investment"]
        categories_expense = ["rent", "utilities", "groceries", "travel", "entertainment", "healthcare"]

        admin_id = seeded_users[0].id
        
        records = []
        
        for _ in range(100):
            record_type = random.choices([RecordType.INCOME, RecordType.EXPENSE], weights=[0.3, 0.7])[0]
            
            if record_type == RecordType.INCOME:
                cat = random.choice(categories_income)
                amt = round(random.uniform(500, 5000), 2)
            else:
                cat = random.choice(categories_expense)
                amt = round(random.uniform(10, 500), 2)
                
           
            days_ago = random.randint(0, 365)
            record_date = (datetime.now() - timedelta(days=days_ago)).date()
            
            records.append(
                FinancialRecord(
                    amount=amt,
                    type=record_type,
                    category=cat,
                    date=record_date,
                    description=f"Auto-generated {cat} transaction",
                    created_by=admin_id
                )
            )
            
        db.add_all(records)
        db.commit()
        
        print("Database seeded successfully!")
        print("\nTest Accounts:")
        for email, _, pwd, role in users_data:
            print(f"Role: {role.value.upper():<8} | Login: {email:<20} | Password: {pwd}")
            
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()
