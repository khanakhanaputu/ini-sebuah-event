import sys
import os

# 1. Tambahkan folder 'src' ke jalur pencarian Python
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

import asyncio
from sqlalchemy import select

# PERBAIKAN DISINI 👇
# Import 'AsyncSessionLocal' sesuai nama di session.py kamu
from app.db.session import AsyncSessionLocal 
from app.models.user import User, PlatformRole

async def promote_user(email: str):
    print(f"🔍 Mencari user: {email}...")
    
    # Gunakan AsyncSessionLocal() dengan kurung ()
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        
        if not user:
            print(f"❌ User dengan email {email} tidak ditemukan! Pastikan sudah login Google dulu.")
            return

        # Cek apakah sudah admin?
        if user.role == PlatformRole.PLATFORM_ADMIN:
            print(f"⚠️ User {email} sudah jadi Admin kok.")
            return

        user.role = PlatformRole.PLATFORM_ADMIN
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        print(f"✅ SUKSES! {email} sekarang adalah SUPER ADMIN! 👑")

if __name__ == "__main__":
    target_email = "juliasta702@gmail.com" 
    
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
    asyncio.run(promote_user(target_email))