from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from sql.engine import async_engine


async def create_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


class Base(DeclarativeBase):
    pass


class Equipment(Base):
    # УСПД
    __tablename__ = 'equipment'

    equipment_id: Mapped[int] = mapped_column(primary_key=True)
    serial: Mapped[str | None] = mapped_column(Text)
    serial_in_sourse: Mapped[str] = mapped_column(Text)
    ip1: Mapped[str] = mapped_column(Text)
    ip2: Mapped[str | None] = mapped_column(Text)
    login: Mapped[str] = mapped_column(Text)
    passw: Mapped[str] = mapped_column(Text)
    bs_type: Mapped[str | None] = mapped_column(Text)
    mode: Mapped[str | None] = mapped_column(Text)
    dl_aver_busyness: Mapped[int | None] = mapped_column(Integer)
    rev_list: Mapped[str | None] = mapped_column(Text)
    latitude: Mapped[str | None] = mapped_column(Text)
    longitude: Mapped[str | None] = mapped_column(Text)
    created_on: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    update_on: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)

    log_equipment: Mapped[list['LogEquipment']] = relationship(back_populates='equipment')
    task: Mapped[list['Task']] = relationship(back_populates='equipment')
    wl: Mapped[list['Wl']] = relationship(back_populates='equipment')
    messages: Mapped[list['Messages']] = relationship(back_populates='equipment')


class Meter(Base):
    # ПУ
    __tablename__ = 'meter'

    meter_id: Mapped[int] = mapped_column(primary_key=True)
    modem: Mapped[int] = mapped_column(Integer)
    hw_type: Mapped[str | None] = mapped_column(Text)
    created_on: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    update_on: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)

    wl: Mapped[list['Wl']] = relationship(back_populates='meter')
    messages: Mapped[list['Messages']] = relationship(back_populates='meter')


class LogEquipment(Base):
    # Лог запросов к УСПД
    __tablename__ = 'log_equipment'

    log_equipment_id: Mapped[int] = mapped_column(primary_key=True)
    # group_task_id: Mapped[int] = mapped_column(Integer, ForeignKey('group_task.group_task_id'))
    task_id: Mapped[int] = mapped_column(Integer, ForeignKey('task.task_id'))
    equipment_id: Mapped[int] = mapped_column(Integer, ForeignKey('equipment.equipment_id'))
    status_response: Mapped[str] = mapped_column(Text)
    # error: Mapped[str | None] = mapped_column(Text)
    response: Mapped[str | None] = mapped_column(Text)
    created_on: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    task: Mapped['Task'] = relationship(back_populates='log_equipment')
    # group_task: Mapped['GroupTask'] = relationship(back_populates='log_equipment')
    equipment: Mapped['Equipment'] = relationship(back_populates='log_equipment')


class Task(Base):
    # Лог запросов к УСПД
    __tablename__ = 'task'

    task_id: Mapped[int] = mapped_column(primary_key=True)
    group_task_id: Mapped[int] = mapped_column(Integer, ForeignKey('group_task.group_task_id'))
    equipment_id: Mapped[int] = mapped_column(Integer, ForeignKey('equipment.equipment_id'))
    type_task: Mapped[str] = mapped_column(Text)
    status_task: Mapped[str] = mapped_column(Text)
    timeouut_task: Mapped[int] = mapped_column(Integer)
    total_time: Mapped[int | None] = mapped_column(Integer)
    error: Mapped[str | None] = mapped_column(Text)
    created_on: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    update_on: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)

    equipment: Mapped['Equipment'] = relationship(back_populates='task')
    group_task: Mapped['GroupTask'] = relationship(back_populates='task')
    log_equipment: Mapped[list['LogEquipment']] = relationship(back_populates='task')


class GroupTask(Base):
    # Лог запросов к УСПД
    __tablename__ = 'group_task'

    group_task_id: Mapped[int] = mapped_column(primary_key=True)
    created_on: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    task: Mapped[list['Task']] = relationship(back_populates='group_task')


class Wl(Base):
    # Связь Белого Списка между УСПД и ПУ
    __tablename__ = 'wl'

    wl_id: Mapped[int] = mapped_column(primary_key=True)
    equipment_id: Mapped[int] = mapped_column(Integer, ForeignKey('equipment.equipment_id'))
    meter_id: Mapped[int] = mapped_column(Integer, ForeignKey('meter.meter_id'))
    last_success: Mapped[int] = mapped_column(Integer)
    present: Mapped[bool] = mapped_column(Boolean)
    created_on: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    update_on: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)

    equipment: Mapped['Equipment'] = relationship(back_populates='wl')
    meter: Mapped['Meter'] = relationship(back_populates='wl')


class Messages(Base):
    # Связь Белого Списка между УСПД и ПУ
    __tablename__ = 'messages'

    messages_id: Mapped[int] = mapped_column(primary_key=True)
    equipment_id: Mapped[int] = mapped_column(Integer, ForeignKey('equipment.equipment_id'))
    meter_id: Mapped[int] = mapped_column(Integer, ForeignKey('meter.meter_id'))
    type_packet: Mapped[int] = mapped_column(Integer)
    time_detected: Mapped[datetime] = mapped_column(DateTime)
    time_saved: Mapped[datetime] = mapped_column(DateTime)
    created_on: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    update_on: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)

    equipment: Mapped['Equipment'] = relationship(back_populates='messages')
    meter: Mapped['Meter'] = relationship(back_populates='messages')
