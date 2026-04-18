from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.calculation import Calculation
from app.schemas.calculation import (
    CalculationCreate,
    CalculationUpdate,
    CalculationResponse,
)

router = APIRouter()


@router.get("/", response_model=list[CalculationResponse])
def browse_calculations(db: Session = Depends(get_db)):
    return db.query(Calculation).all()


@router.get("/{calculation_id}", response_model=CalculationResponse)
def read_calculation(calculation_id, db: Session = Depends(get_db)):
    calculation = db.query(Calculation).filter(Calculation.id == calculation_id).first()
    if not calculation:
        raise HTTPException(status_code=404, detail="Calculation not found")
    return calculation


@router.post("/", response_model=CalculationResponse)
def add_calculation(data: CalculationCreate, db: Session = Depends(get_db)):
    calculation = Calculation.create(
        calculation_type=data.type,
        user_id=data.user_id,
        inputs=data.inputs
    )
    calculation.result = calculation.get_result()
    db.add(calculation)
    db.commit()
    db.refresh(calculation)
    return calculation


@router.put("/{calculation_id}", response_model=CalculationResponse)
def edit_calculation(calculation_id, data: CalculationUpdate, db: Session = Depends(get_db)):
    calculation = db.query(Calculation).filter(Calculation.id == calculation_id).first()
    if not calculation:
        raise HTTPException(status_code=404, detail="Calculation not found")

    if data.inputs is not None:
        calculation.inputs = data.inputs
        calculation.result = calculation.get_result()

    db.commit()
    db.refresh(calculation)
    return calculation


@router.delete("/{calculation_id}")
def delete_calculation(calculation_id, db: Session = Depends(get_db)):
    calculation = db.query(Calculation).filter(Calculation.id == calculation_id).first()
    if not calculation:
        raise HTTPException(status_code=404, detail="Calculation not found")

    db.delete(calculation)
    db.commit()
    return {"message": "Calculation deleted successfully"}