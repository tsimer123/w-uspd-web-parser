import json
from datetime import datetime

from aiohttp import ClientSession, CookieJar

from base_http.base import BaseRequest
from data_class.data_get_command import EquipmentInfoModel, GetComandModel, MeterWlAllModel, MeterWlModel
from sql.model import (
    TaskEquipmentHandlerModelGet,
)


async def get_wl(task_rb: TaskEquipmentHandlerModelGet) -> GetComandModel:
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
                    result.meter_wl = await get_meter_wl(con)
                    if result.meter_wl.status is True:
                        result.status_task = 'true'
                    else:
                        result.error = result.meter_wl.error
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


async def get_meter_wl(con: BaseRequest) -> MeterWlAllModel:
    """Функция запрапшивает номер УСПД, если вернет None, то это не штатная ситуация"""
    result = MeterWlAllModel(status=False)
    # param_count_wl = 'total=true&limit=0'
    # count_meters_in_wl = await con.get_request_with_params_waviot('gateway/localid', param_count_wl)
    try:
        # if count_meters_in_wl.status is True:
        # param_wl = 'offset=32&limit=32'
        param_wl = ''
        meter_wl = await con.get_request_with_params_waviot('telecom/api/device', param_wl)
        if meter_wl.status is True:
            meter_wl.data = json.loads(meter_wl.data)
            result.meter_wl = []
            for line in meter_wl.data:
                result.meter_wl.append(
                    MeterWlModel(
                        number=line['modem_id'],
                        hw_type=line['hw_type'],
                        last_success_dl_ts=line['last_success_dl_ts'],
                    )
                )
            result.status = True
        else:
            result.error = str(meter_wl.error)
        # else:
        #     result.error = str(count_meters_in_wl.error)
    except Exception as ex:
        result.error = str(ex.args)
    return result
