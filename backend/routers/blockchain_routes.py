from fastapi import APIRouter, Depends, HTTPException
from backend.models import User
from backend.schemas import ContractChangeRequest
from backend.services.auth import get_current_user
from backend.blockchain.blockchain_func import Blockchain

router = APIRouter()

# Создаем экземпляр Blockchain
blockchain = Blockchain()

# Добавление изменения контракта
@router.post("/add_contract_change/")
async def add_contract_change(request: ContractChangeRequest, current_user: User = Depends(get_current_user)):
    user = blockchain.get_user(request.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    blockchain.add_contract_change(request.username, request.contract_data)
    return {"message": "Contract change added to blockchain"}

# Логирование доступа
@router.post("/log_data_access/")
async def log_data_access(username: str, key: str, current_user: User = Depends(get_current_user)):
    target_user = blockchain.get_user(username)
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    if not blockchain.check_access(current_user, key):
        raise HTTPException(status_code=403, detail="Access denied")
    blockchain.log_data_access(current_user, target_user, key)
    return {"message": "Access logged successfully"}


# Майнинг блока
@router.post("/mine_block/")
async def mine_block(data: str):
    if not blockchain.is_chain_valid():
        raise HTTPException(status_code=400, detail="Blockchain is invalid")
    block = blockchain.mine_block(data=data)
    return block
