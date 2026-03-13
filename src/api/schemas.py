from pydantic import BaseModel


class DeviceBase(BaseModel):
    state: str
    ip4: str
    mac: str
    vendor: str
    os_name: str
    os_accuracy: int
    last_boot: str
    device_guess: str
    device_guess_accuracy: str


class DeviceCreate(DeviceBase):
    pass


class Device(DeviceBase):
    id: int

    class Config:
        from_attributes = True


class PortBase(BaseModel):
    number: int
    protocol: str
    state: str
    service_name: str
    service_product: str


class PortCreate(PortBase):
    pass


class Port(PortBase):
    id: int

    class Config:
        from_attributes = True


class ScanBase(BaseModel):
    timestamp: str


class ScanCreate(ScanBase):
    pass


class Scan(ScanBase):
    id: int

    class Config:
        orm_mode = True
