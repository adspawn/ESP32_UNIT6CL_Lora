#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UNIT-C6L (Meshtastic) USB シリアル受信

受信側: UNIT-C6L を PC に USB 接続するだけ
送信側: ESP32-C6 + UNIT-C6L (10秒長押しで G4 -> LoRa 送信)

使い方:
  pip install -r requirements.txt
  python receive_serial.py
  python receive_serial.py --port COM5
  python receive_serial.py --list
"""

import argparse
import sys
import time
from datetime import datetime

try:
    import serial.tools.list_ports
except ImportError:
    print("pyserial が未インストールです: pip install pyserial")
    sys.exit(1)

try:
    import meshtastic.serial_interface
    from pubsub import pub
except ImportError:
    print("meshtastic が未インストールです: pip install meshtastic")
    sys.exit(1)


def list_ports() -> None:
    """利用可能なシリアルポートを一覧表示"""
    ports = list(serial.tools.list_ports.comports())
    if not ports:
        print("シリアルポートが見つかりません")
        return

    print("利用可能なポート:")
    for p in ports:
        print(f"  {p.device:8}  {p.description}")


def format_time() -> str:
    return datetime.now().strftime("%H:%M:%S")


def on_receive(packet: dict, interface=None) -> None:
    """Meshtastic 受信パケットを表示"""
    ts = format_time()

    from_id = packet.get("fromId", "?")
    to_id = packet.get("toId", "?")
    snr = packet.get("rxSnr", "-")
    rssi = packet.get("rxRssi", "-")

    decoded = packet.get("decoded", {})
    portnum = decoded.get("portnum", "")

    # テキストメッセージ (Detection Sensor 等)
    text = decoded.get("text")
    if text:
        print(f"[{ts}] *** 受信 ***")
        print(f"  送信元 : {from_id}")
        print(f"  宛先   : {to_id}")
        print(f"  種別   : {portnum}")
        print(f"  本文   : {text}")
        print(f"  SNR    : {snr} dB  /  RSSI: {rssi} dBm")
        print()
        return

    # その他のデコード済みデータ
    if decoded:
        print(f"[{ts}] パケット受信")
        print(f"  送信元 : {from_id}")
        print(f"  種別   : {portnum}")
        if "data" in decoded:
            print(f"  データ : {decoded['data']}")
        print(f"  SNR    : {snr} dB  /  RSSI: {rssi} dBm")
        print()
        return

    # デコードできないパケット (簡易表示)
    print(f"[{ts}] 生パケット (from={from_id}, to={to_id})")


def on_connection(interface, topic=None) -> None:
    print(f"[{format_time()}] UNIT-C6L に接続しました")
    if hasattr(interface, "myInfo") and interface.myInfo:
        node_id = getattr(interface.myInfo, "my_node_num", None)
        if node_id is not None:
            print(f"  自ノード ID: {node_id}")
    print("受信待機中... (Ctrl+C で終了)\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="UNIT-C6L USB シリアル受信 (Meshtastic)"
    )
    parser.add_argument(
        "--port", "-p",
        help="シリアルポート (例: COM5)。省略時は自動検出",
    )
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="シリアルポート一覧を表示して終了",
    )
    args = parser.parse_args()

    if args.list:
        list_ports()
        return

    print("=== UNIT-C6L シリアル受信 ===")
    if args.port:
        print(f"ポート: {args.port}")
    else:
        print("ポート: 自動検出")
        list_ports()
        print()

    pub.subscribe(on_receive, "meshtastic.receive")
    pub.subscribe(on_connection, "meshtastic.connection.established")

    try:
        if args.port:
            iface = meshtastic.serial_interface.SerialInterface(devPath=args.port)
        else:
            iface = meshtastic.serial_interface.SerialInterface()
    except Exception as e:
        print(f"接続エラー: {e}")
        print("\n対処:")
        print("  1. UNIT-C6L が USB 接続されているか確認")
        print("  2. 他のアプリ (Meshtastic アプリ等) を閉じる")
        print("  3. python receive_serial.py --list でポート名を確認")
        print("  4. python receive_serial.py --port COMx で指定")
        sys.exit(1)

    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        print(f"\n[{format_time()}] 終了")
    finally:
        iface.close()


if __name__ == "__main__":
    main()
