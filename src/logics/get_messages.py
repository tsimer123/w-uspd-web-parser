import json
from datetime import datetime

from aiohttp import ClientSession, CookieJar

from base_http.base import BaseRequest
from data_class.data_get_command import (
    EquipmentInfoModel,
    GetComandModel,
    MeterPacketAllModel,
    MeterPacketBsAllModel,
    MeterPacketBsModel,
    MeterPacketModel,
    MeterWlAllModel,
)
from db_handler import get_max_time_saved_bs_filter_equipment
from sql.model import TaskEquipmentHandlerModelGet


async def get_messages(task_rb: TaskEquipmentHandlerModelGet) -> GetComandModel:
    start_time = datetime.now()
    print(
        f'{datetime.now()}: start get data for task {task_rb.task_id}, equipment {task_rb.serial_in_sourse}, command: {task_rb.type_task}'
    )
    result = GetComandModel(
        task_id=task_rb.task_id,
        equipment_id=task_rb.equipment_id,
        type_task=task_rb.type_task,
        status_task='false',
    )
    # включаем хранение куки для ip адресов
    cookiejar = CookieJar(unsafe=True)
    # создаем список ip адресов УСПД
    list_ip = [task_rb.ip1]
    if task_rb.ip2 is not None:
        list_ip.append(task_rb.ip2)
    # создаем подключени
    async with ClientSession(cookie_jar=cookiejar) as session:
        # пытаемся подключится к УСПД
        for ip in list_ip:
            con = BaseRequest(
                session,
                ip,
                task_rb.login,
                task_rb.passw,
            )
            # получаем токен авторизации
            auth = await con.get_auth_waviot()
            if auth.status is True:
                break
        if auth.status is True:
            # token = auth.data
            try:
                # получаем данные по УСПД
                result.equipment_info = await get_local_id(con)
                if result.equipment_info.status is True:
                    if task_rb.type_task == 'get_messages':
                        result.meter_packet = await get_packet(con)
                        if result.meter_packet.status is True:
                            result.status_task = 'true'
                        else:
                            result.error = result.meter_packet.error
                    if task_rb.type_task == 'get_messages_bs':
                        result.meter_packet_bs = await get_packet_bs(
                            con, result.equipment_id, result.equipment_info.serial
                        )
                        if result.meter_packet_bs.status is True:
                            result.status_task = 'true'
                        else:
                            result.error = result.meter_packet_bs.error
                    # if result.meter_packet.status is True:
                    #         result.status_task = 'true'
                    # else:
                    #     result.error = result.meter_packet.error
                else:
                    result.error = result.equipment_info.error
            except Exception as ex:
                result.error = str(ex.args)
        else:
            print('????')
            print(str(auth.error))
            result.error = str(auth.error)
    end_time = datetime.now()
    delta = end_time - start_time
    result.total_time = round(delta.total_seconds())
    return result


async def get_local_id(con: BaseRequest) -> EquipmentInfoModel:
    """Функция запрапшивает номер УСПД, если вернет None, то это не штатная ситуация"""
    result = EquipmentInfoModel(status=False, date_response=datetime.now())
    serial = await con.get_request_waviot('gateway/localid')
    try:
        if serial.status is True:
            serial.data = json.loads(serial.data)
            result.serial = serial.data['id']
            param_uspd = f'?bs_ids={result.serial}'
            uspd_info = await con.get_request_with_params_waviot('telecom/api/bs', param_uspd)
            uspd_info.data = json.loads(uspd_info.data)
            if uspd_info.status is True:
                trigger_equipment = 0
                for line_uspd in uspd_info.data:
                    if line_uspd['bs_id'] == serial.data['id']:
                        if 'bs_type' in line_uspd:
                            result.bs_type = line_uspd['bs_type']
                        if 'mode' in line_uspd:
                            result.mode = line_uspd['mode']
                        if 'dl_aver_busyness' in line_uspd:
                            result.dl_aver_busyness = line_uspd['dl_aver_busyness']
                        if 'rev_list' in line_uspd:
                            result.rev_list = (',').join(line_uspd['rev_list'])
                        if 'latitude' in line_uspd:
                            result.latitude = line_uspd['latitude']
                        if 'longitude' in line_uspd:
                            result.longitude = line_uspd['longitude']
                        trigger_equipment = 1
                        result.status = True
                        break
                if trigger_equipment == 0:
                    result.error = 'not number equipment in response'
        else:
            result.error = 'bad response on equipment'
    except Exception as ex:
        result.error = str(ex.args)
    return result


async def get_packet(con: BaseRequest) -> MeterWlAllModel:
    """Функция запрапшивает из УСПД эфир обмена с ПУ"""
    result = MeterPacketAllModel(status=False)
    ts_now = int(round(datetime.timestamp(datetime.now())))
    ts_start = ts_now - (86400 * 2)
    offset = 0
    type_packet = 3
    limit_packet = 10000
    try:
        trigger_packet = 0
        temp_packet = []
        while trigger_packet == 0:
            param_packet = (
                f'timefrom={ts_start}&timeto={ts_now}&message_types={type_packet}&limit={limit_packet}&offset={offset}'
            )
            meter_packet = await con.get_request_with_params_waviot('telecom/api/messages', param_packet)
            if meter_packet.status is True:
                meter_packet.data = json.loads(meter_packet.data)
                for line in meter_packet.data:
                    temp_packet.append(
                        MeterPacketModel(
                            uspd_serial=line['bs_id'],
                            number=line['modem_id'],
                            type_packet=line['type'],
                            time_detected=line['time_detected'],
                            time_saved=line['time_saved'],
                        )
                    )
                result.status = True
                if len(meter_packet.data) == limit_packet:
                    offset = offset + limit_packet
                else:
                    trigger_packet = 1
                    result.meter_packet = temp_packet

            else:
                result.error = str(meter_packet.error)
        # else:
        #     result.error = str(count_meters_in_wl.error)
    except Exception as ex:
        result.error = str(ex.args)
    return result


async def get_packet_bs(con: BaseRequest, equipment_id: int, bs_id: int) -> MeterWlAllModel:
    """Функция запрапшивает из УСПД эфир обмена с ПУ"""
    result = MeterPacketBsAllModel(status=False)
    max_time_saved_bs = await get_max_time_saved_bs_filter_equipment(equipment_id)

    # max_time_saved_bs = datetime.now() - timedelta(seconds=600)

    end_datetime = int(round(datetime.timestamp(datetime.now())))
    ts_start = (
        (int(round(datetime.timestamp(max_time_saved_bs))))
        if max_time_saved_bs is not None
        else (int(round(datetime.timestamp(datetime(datetime.now().year, datetime.now().month, datetime.now().day)))))
        - 60
    )
    type_packet = '0,1'
    limit_packet = 10000
    try:
        temp_packet = []
        while ts_start < end_datetime:
            ts_start = ts_start + (60)
            # print(f'{bs_id} - {datetime.fromtimestamp(ts_start)}')
            ts_end = ts_start + (60)
            param_packet = f'id={bs_id}&from={ts_start}&to={ts_end}&types={type_packet}&limit={limit_packet}'

            meter_packet = await con.get_request_with_params_waviot('gateway/messages', param_packet)

            if meter_packet.status is True:
                meter_packet.data = json.loads(meter_packet.data)
                # print(f'{bs_id} - {len(meter_packet.data)}')
                for line in meter_packet.data:
                    temp_packet.append(
                        MeterPacketBsModel(
                            uspd_serial=bs_id,
                            number=line['modem_id'],
                            freq=line['freq'],
                            iterator=line['iterator'],
                            offset=line['offset'],
                            payload=line['payload'],
                            phy=line['phy'],
                            type_packet=line['type'],
                            time_saved=line['time_saved'],
                            nsnr=line['nsnr'],
                            rssi_or_pwr=line['rssi_or_pwr'],
                            snr=line['snr'],
                        )
                    )
            else:
                result.error = str(meter_packet.error)
        if result.error is None:
            result.status = True
        if len(temp_packet) > 0:
            result.meter_packet_bs = temp_packet
    except Exception as ex:
        result.error = str(ex.args)
    return result
