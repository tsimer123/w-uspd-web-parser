import argparse


def get_args() -> dict:
    parser = argparse.ArgumentParser(description='Скрипт по вычитки параметров с УСПД Нартис')

    parser.add_argument(
        '-t', '--type', help='тип запуска', required=True, type=str, choices=['continue', 'restart', 'clear']
    )
    parser.add_argument(
        '-i',
        '--interval',
        help='интервал перезапуска, в сек. (по умолчанию 3600 с)',
        required=False,
        type=int,
        default=3600,
    )
    parser.add_argument(
        '-qc', '--queue_count', help='размер очереди (по умолчанию 1000)', required=False, type=int, default=1000
    )
    parser.add_argument(
        '-hc',
        '--handler_count',
        help='количество обработчиков (по умолчанию 750)',
        required=False,
        type=int,
        default=750,
    )
    parser.add_argument(
        '-tz',
        '--time_zone',
        help='часовой пояс (по умолчанию 3)',
        required=False,
        type=int,
        default=3,
    )

    args = parser.parse_args()
    args = vars(args)

    return args
