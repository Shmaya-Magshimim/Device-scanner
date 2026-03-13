from typing import List
from sqlalchemy.orm import Session
from ..api import DeviceCreate, PortCreate, ScanCreate
from .models import Port, Device, Scans


def save_device(db: Session, device: DeviceCreate) -> Device:
    db_device = Device(**device.model_dump())
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device


def save_ports(db: Session, ports: List[PortCreate], device_id: int) -> None:
    for port in ports:
        db_port = Port(**port.model_dump(), device_id=device_id)
        db.add(db_port)

    db.commit()


def get_device(db: Session, device_id: int) -> Device:
    return db.query(Device).filter(Device.id == device_id).first()


def get_devices(db: Session, skip: int = 0, limit: int = 100) -> list:
    return db.query(Device).offset(skip).limit(limit).all()


def get_ports_by_device_id(db: Session, device_id: int) -> list:
    return db.query(Port).filter(Port.device_id == device_id).all()


def create_scan(db: Session, scan: ScanCreate) -> Scans:
    db_scan = Scans(**scan.model_dump())
    db.add(db_scan)
    db.commit()
    db.refresh(db_scan)
    return db_scan
