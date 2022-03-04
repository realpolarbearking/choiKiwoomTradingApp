from api.Kiwoom import *
from util.time_helper import *
from util.notifier import *
import math
import traceback


class CHOIStrategy(QThread):

    def __init__(self):
        QThread.__init__(self)
        self.strategy_name = "CHOIStrategy"
        self.kiwoom = Kiwoom()

        # 계좌 예수금
        self.deposit = 0

        # 초기화 함수 성공 여부 확인 변수
        self.is_init_success = False

        self.init_strategy()

    def init_strategy(self):
        """전략 초기화 기능을 수행하는 함수"""
        try:

            # Kiwoom > 주문정보 확인
            self.kiwoom.get_order()

            # Kiwoom > 잔고 확인
            self.kiwoom.get_balance()

            # Kiwoom > 예수금 확인
            self.deposit = self.kiwoom.get_deposit()

            #for Testing BuyCondition
            self.userIndex = "001"
            self.conditonIndex = self.kiwoom.condition_list['index'].index(self.userIndex)
            self.kiwoom.sendCondition("0156", self.kiwoom.condition_list['name'][self.conditonIndex], int(self.userIndex), 1)

            #self.set_universe_real_time()

            self.is_init_success = True

        except Exception as e:
            print(traceback.format_exc())
            # LINE 메시지를 보내는 부분
            #send_message(traceback.format_exc(), RSI_STRATEGY_MESSAGE_TOKEN)

    def run(self):
        """실질적 수행 역할을 하는 함수"""
        while self.is_init_success:
            try:
                #For testing
                # self.get_balance_count()
                # self.get_buy_order_count()
                # self.kiwoom.returnFilteredCodes()
                # self.kiwoom.returnSellFilteredCodes()
                #self.set_universe_real_time()
                # (0)장중인지 확인
                if not check_transaction_open():
                    print("장시간이 아니므로 5분간 대기합니다.")
                    time.sleep(5 * 60)
                    continue

                # SELL_LOOP [*Check for balance status first (Only sell when there are stocks in the account)]
                for code in self.kiwoom.balance.keys(): # 보유 주식을 대상으로,
                    time.sleep(0.5)

                    if len(self.kiwoom.balance.keys()) < 1:
                        return

                    # (1) 접수한 매도 주문이 있는지 확인 또는 매도 주문은 종료되었지만 보유 주식에 남아 있고 보유 수량은 0인 경우
                    # self.kiwoom.order[code]['매도수구분'] == 0
                    if (code in self.kiwoom.order.keys() and self.kiwoom.order[code]['주문구분'] == "매도"): #or (self.kiwoom.balance[code]['보유수량'] == 0):
                        # (2) (1)의 경우, 프린트로 문구 출력
                        print('매도 주문 존재: ', self.kiwoom.order[code])
                        # (2.1) '미체결수량' 확인하여 미체결 종목인지 확인 (매도)
                        if self.kiwoom.order[code]['미체결수량'] > 0:
                            pass
                    # 매도 신호가 나오면,
                    elif self.check_sell_signal(code):
                        # 매도 주문 넣기
                        self.order_sell(code)

                # BUY LOOP
                for code in self.kiwoom.returnFilteredCodes():
                    time.sleep(0.5)
                    # (1)접수한 주문이 있는지 확인
                    if code in self.kiwoom.order.keys() and self.kiwoom.order[code]['주문구분'] == "매수" \
                            and self.kiwoom.order[code]['미체결수량'] > 0:
                        print('매수 주문 존재: ', str(self.kiwoom.order[code]) + " 주문상태: " + str(self.kiwoom.order[code]['주문상태']))
                        # (2.1) '미체결수량' 확인하여 미체결 종목인지 확인
                        # if self.kiwoom.order[code]['미체결수량'] > 0:
                        #     pass
                    # (3)보유 종목인지 확인
                    elif code in self.kiwoom.balance.keys():
                        print('보유 종목', self.kiwoom.balance[code])
                    else:
                        self.check_buy_signal_and_order(code)

            except Exception as e:
                print(traceback.format_exc())
                # LINE 메시지를 보내는 부분
                # send_message(traceback.format_exc(), RSI_STRATEGY_MESSAGE_TOKEN)

    def set_universe_real_time(self, code):
        """유니버스 실시간 체결정보 수신 등록하는 함수"""
        # 임의의 fid를 하나 전달하기 위한 코드(아무 값의 fid라도 하나 이상 전달해야 정보를 얻어올 수 있음)
        fids = get_fid("체결시간")
        # 장운영구분을 확인하고 싶으면 사용할 코드
        # self.kiwoom.set_real_reg("1000", "", get_fid("장운영구분"), "0")
        code = code
        # 화면번호 9999에 종목코드들의 실시간 체결정보 수신을 요청
        self.kiwoom.set_real_reg("9999", code, fids, "1")


    # def set_universe_real_time(self):
    #     #유니버스 실시간 체결정보 수신 등록하는 함수
    #     # 임의의 fid를 하나 전달하기 위한 코드(아무 값의 fid라도 하나 이상 전달해야 정보를 얻어올 수 있음)
    #     fids = get_fid("체결시간")
    #
    #     # 장운영구분을 확인하고 싶으면 사용할 코드
    #     # self.kiwoom.set_real_reg("1000", "", get_fid("장운영구분"), "0")
    #
    #     kospi = self.kiwoom.get_code_list_by_market("0")
    #     kosdaq = self.kiwoom.get_code_list_by_market("10")
    #
    #     # universe 딕셔너리의 key값들은 종목코드들을 의미
    #     #codes = kospi + kosdaq
    #     codes = list(set(self.kiwoom.returnFilteredCodes() + list(self.kiwoom.balance.keys())))
    #     codesLen = len(codes)
    #
    #     # 종목코드들을 ';'을 기준으로 묶어주는 작업
    #     codes = ";".join(map(str, codes))
    #     print("유니버스_종목코드 " + "(총: " + str(codesLen) + "개): " + str(codes))
    #     # 화면번호 9999에 종목코드들의 실시간 체결정보 수신을 요청
    #     self.kiwoom.set_real_reg("9999", codes, fids, "0")


    def check_sell_signal(self, code):
        """매도대상인지 확인하는 함수"""

        # (1)현재 체결정보가 존재하지 않는지 확인
        if code not in self.kiwoom.universe_realtime_transaction_info.keys():
            # 체결 정보가 없으면 더 이상 진행하지 않고 함수 종료
            print(str(code) + ": " + "매도대상 확인 과정에서 아직 체결정보가 없습니다.")
            return

        # 매도 조건 두 가지를 모두 만족하면 True
        if code in self.kiwoom.returnSellFilteredCodes():
            print("YES_SELL " + str(code))
            return True
        else:
            return False

    def order_sell(self, code):
        """매도 주문 접수 함수"""
        # 보유 수량 확인(전량 매도 방식으로 보유한 수량을 모두 매도함)
        quantity = self.kiwoom.balance[code]['보유수량']

        # 최우선 매도 호가 확인
        ask = self.kiwoom.universe_realtime_transaction_info[code]['(최우선)매도호가']

        order_result = self.kiwoom.send_order('send_sell_order', '1001', 2, code, quantity, ask, '00')
        # _on_chejan_slot가 늦게 동작할 수도 있기 때문에 미리 약간의 정보를 넣어둠
        self.kiwoom.order[code] = {'주문구분': '매도', '미체결수량': quantity}

        # # LINE 메시지를 보내는 부분
        # message = "[{}]sell order is done! quantity:{}, ask:{}, order_result:{}".format(code, quantity, ask, order_result)
        # send_message(message, RSI_STRATEGY_MESSAGE_TOKEN)

    def check_buy_signal_and_order(self, code):
        """매수 대상인지 확인하고 주문을 접수하는 함수"""
        # 매수 가능 시간 확인
        if not check_transaction_open():
            return False

        # (1)현재 체결정보가 존재하지 않는지 확인
        if code not in self.kiwoom.universe_realtime_transaction_info.keys():
            # 존재하지 않다면 더이상 진행하지 않고 함수 종료
            self.set_universe_real_time(code)
            print(str(code) + ": " + "매수대상 확인 과정에서 아직 체결정보가 없습니다.")
            return

        #for testing BuyCondition
        print("arr" + str(self.kiwoom.universe_realtime_transaction_info.keys()))
        print("balancearr" + str(self.kiwoom.balance.keys()))

        # (2)매수 신호 확인(조건에 부합하면 주문 접수)
        if code in self.kiwoom.returnFilteredCodes():

            # if code not in self.myUniverse: # 코드가 유니버스에 없을시
            #     print("종목이 유니버스에 존재하지 않습니다.")
            #     return

            # (3)이미 보유한 종목, 매수 주문 접수한 종목의 합이 보유 가능 최대치(10개)라면 더 이상 매수 불가하므로 종료
            if (self.get_balance_count() + self.get_buy_order_count()) >= 10:
                return

            # (4)주문에 사용할 금액 계산(10은 최대 보유 종목 수로써 consts.py에 상수로 만들어 관리하는 것도 좋음)
            budget = self.deposit / (10 - (self.get_balance_count() + self.get_buy_order_count()))

            # 최우선 매도호가 확인
            bid = self.kiwoom.universe_realtime_transaction_info[code]['(최우선)매수호가']

            # (5)주문 수량 계산(소수점은 제거하기 위해 버림)
            quantity = math.floor(budget / bid)

            # (6)주문 주식 수량이 1 미만이라면 매수 불가하므로 체크
            if quantity < 1:
                return

            # (7)현재 예수금에서 수수료를 곱한 실제 투입금액(주문 수량 * 주문 가격)을 제외해서 계산
            amount = quantity * bid
            self.deposit = math.floor(self.deposit - amount * 1.00015)

            # (8)예수금이 0보다 작아질 정도로 주문할 수는 없으므로 체크
            if self.deposit < 0:
                return

            # (8)계산을 바탕으로 지정가 매수 주문 접수
            order_result = self.kiwoom.send_order('send_buy_order', '1001', 1, code, quantity, bid, '00')

            # _on_chejan_slot가 늦게 동작할 수도 있기 때문에 미리 약간의 정보를 넣어둠
            self.kiwoom.order[code] = {'주문구분': '매수', '미체결수량': quantity}

            # LINE 메시지를 보내는 부분
            # message = "[{}]buy order is done! quantity:{}, bid:{}, order_result:{}, deposit:{}, get_balance_count:{}, get_buy_order_count:{}, balance_len:{}".format(
            #     code, quantity, bid, order_result, self.deposit, self.get_balance_count(), self.get_buy_order_count(),
            #     len(self.kiwoom.balance))
            # send_message(message, RSI_STRATEGY_MESSAGE_TOKEN)

        # 매수신호가 없다면 종료
        else:
            print(str(code) + " can not be processed.")
            return

    def get_balance_count(self):
        """매도 주문이 접수되지 않은 보유 종목 수를 계산하는 함수"""
        balance_count = len(self.kiwoom.balance)
        # kiwoom balance에 존재하는 종목이 매도 주문 접수되었다면 보유 종목에서 제외시킴
        for code in self.kiwoom.order.keys():
            if code in self.kiwoom.balance and self.kiwoom.order[code]['주문구분'] == "매도" and self.kiwoom.order[code]['미체결수량'] == 0:
                balance_count = balance_count - 1
        print("balance_count: " + str(balance_count))
        return balance_count

    def get_buy_order_count(self):
        """매수 주문 종목 수를 계산하는 함수"""
        buy_order_count = 0
        # 아직 체결이 완료되지 않은 매수 주문
        for code in self.kiwoom.order.keys():
            # for testing BuyCondition
            # print("arr" + str(self.kiwoom.universe_realtime_transaction_info.keys()))
            # print("balancearr" + str(self.kiwoom.balance.keys()))
            # print("주문코드: " + str(code))
            # print(" 주문상태: " + str(self.kiwoom.order[code]['주문상태']))
            if code not in self.kiwoom.balance and self.kiwoom.order[code]['주문구분'] == "매수" \
                    and self.kiwoom.order[code]['미체결수량'] > 0:
                buy_order_count = buy_order_count + 1
        print("buy_order_count: " + str(buy_order_count))
        return buy_order_count