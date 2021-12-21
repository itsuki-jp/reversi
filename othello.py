import copy
import sys

EMPTY = 9
WHITE = 0  # WhiteがCPU
BLACK = 1  # BLACKが人間
H = 8  # 盤面のサイズ
W = 8  # 盤面のサイズ
TOTAL = 8 * 8  # 盤面における駒の最大数
MIN_VAL = -1000
MAX_VAL = 100
DEPTH = 3  # n手読みの場合は、(n-1)にする
INF = float("inf")

WEIGHT = [[40, -12, 0, -1, -1, 0, -12, 40],
          [-12, -15, -3, -3, -3, -3, -15, -12],
          [0, -3, 0, -1, -1, 0, -3, 0],
          [-1, -3, -1, -1, -1, -1, -3, -1],
          [-1, -3, -1, -1, -1, -1, -3, -1],
          [0, -3, 0, -1, -1, 0, -3, 0],
          [-12, -15, -3, -3, -3, -3, -15, -12],
          [40, -12, 0, -1, -1, 0, -12, 40]]


class State:
    def __init__( self, board, cnt, turn, black, white ):
        """盤面の状態とか

        :param board: 盤面の状態
        :param cnt: 盤面に何個おいてあるか
        :param turn: 自分・敵のどっちの番か
        :param black: 黒の数
        :param white: 白の数
        """
        self.board = board
        self.cnt = cnt
        self.turn = turn
        self.black = black
        self.white = white


def show_winner( state ):
    """勝者を表示
    
    :param state: 盤面の状態
    :return: None
    """
    res = "Winner is "
    black = state.black
    white = state.white
    if black > white:
        res += "BLACK"
    elif black < white:
        res += "WHITE"
    else:
        res = "DRAW"
    print(res)
    exit()


def display( board ):
    """盤面を表示

    :param board: 盤面
    :type board: list[list[int]]
    """
    #  盤面を表示
    dis = [["-", 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']]
    for _ in range(H):
        temp = ["-" if t == 9 else t for t in board[_]]
        dis.append([_ + 1] + temp)
    for i in dis:
        print(*i)


def end_check( state ):
    """終了確認

    :param state: 現在の手数
    :type state: State
    :return: True if 盤面が埋まった else False
    """
    if state.cnt == TOTAL:
        return True
    state2 = copy.deepcopy(state)
    state2.turn ^= 1
    _, TF2 = put_able(state2)
    if not TF2:
        return True
    return False


def put_able( state ):
    """置ける場所を全探索

    :param state: 盤面の状態
    :type state: State
    :return: 置ける場所の辞書
    """
    res = dict()
    TF = False
    for y in range(H):
        for x in range(W):
            if state.board[y][x] != EMPTY:
                continue
            temp = chose_able(state, x, y)
            if temp:
                res[(x, y)] = temp
                TF = True
    return res, TF


def chose_able( state, x, y ):
    """(x,y)に置けるかどうか

    :param state: 盤面の状態
    :param x: 置く場所のx座標
    :param y: 置く場所のy座標
    :return: (x,y)における場合はひっくり返りた盤面(State)、おけない場合はFalse
    """
    board = state.board
    turn = state.turn
    TF = False
    temp = []  # [(i,j),歩数]
    state_copy = state
    for i, j in [(1, 0), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1), (0, 1), (0, -1)]:
        end_found = False
        nx, ny = x + i, y + j
        cnt = 0
        while 0 <= nx < W and 0 <= ny < H:
            cnt += 1
            if cnt > 1 and board[ny][nx] == turn:
                end_found = True
                TF = True
                break
            if board[ny][nx] != turn ^ 1:
                break
            nx += i
            ny += j
        if end_found:
            temp.append([(i, j), cnt])
    if TF:
        return flip(state_copy, temp, x, y)
    else:
        return False


def flip( state, lst, x, y ):
    """(x,y)においた時に、ひっくり返す

    :param state: 盤面の状態
    :param lst: [(i,j),歩数]のリスト
    :param x: 置く場所のx座標
    :param y: 置く場所のy座標
    :return: ひっくり返した時の盤面の状態
    """
    board = copy.deepcopy(state.board)
    turn = state.turn
    flip_cnt = 0
    for ij, cnt in lst:
        flip_cnt += cnt - 1
        i, j = ij
        nx, ny = x, y
        for _ in range(cnt):
            board[ny][nx] = turn
            nx += i
            ny += j
    if turn == BLACK:
        res = State(board, state.cnt + 1, turn ^ 1, state.black + flip_cnt + 1, state.white - flip_cnt)
    else:
        res = State(board, state.cnt + 1, turn ^ 1, state.black - flip_cnt, state.white + flip_cnt + 1)
    return res


def neg_max( state, depth, alpha, beta ):
    """ネガマックス法

    :param state: 盤面の状態
    :param depth: 深さ
    :param alpha: alpha
    :param beta: beta
    """
    if depth == DEPTH:
        return evaluation(state)
    possible_pos, TF = put_able(state)
    if not TF:
        return MIN_VAL
    best_num = -INF
    best_state = None
    best_way = None
    for nxt in list(possible_pos):
        val = -neg_max(possible_pos[nxt], depth + 1, -beta, -alpha)
        if val >= beta and depth != 0:
            return val
        if val > best_num:
            best_num = val
            alpha = max(alpha, best_num)
            best_way = nxt
            best_state = possible_pos[nxt]
    if depth == 0:
        return best_state, best_way
    else:
        return best_num


def evaluation( state ):
    """評価関数
    
    :param state: 盤面の状態
    :return: 評価値
    """
    turn = state.turn
    board = state.board
    res = 0
    for i in range(H):
        for j in range(W):
            if board[i][j] == turn ^ 1:
                res += WEIGHT[i][j]
            elif board[i][j] == turn:
                res -= WEIGHT[i][j]
    return -res


def convert_way( x, y ):
    """(1,1)のような打つ手を(b,2)に変換する

    :param x: 打つ場所のx座標
    :param y: 打つ場所のy座標
    :return: 変換した打ち手
    """
    yoko = "abcdefgh"
    tate = "12345678"
    return str(yoko[x] + tate[y])


def convert_user2num( way ):
    """(b,2)を(1,1)に変換

    :param way: 打ち手
    :return: 変換した打ち手
    """
    if len(way) != 2:
        return False
    x, y = way
    y = int(y) - 1
    yoko = "abcdefgh"
    if x not in yoko or not 0 <= y < W:
        return False
    x = yoko.index(x)
    return (x, y)


def main():
    #  初期盤面を作成
    board = [[EMPTY for _ in range(W)] for _ in range(H)]
    board[H // 2][W // 2] = WHITE
    board[H // 2 - 1][W // 2 - 1] = WHITE
    board[H // 2 - 1][W // 2] = BLACK
    board[H // 2][W // 2 - 1] = BLACK
    state = State(board, 4, WHITE, 2, 2)
    
    while True:
        #  色々と出力する
        print("--------------------")
        print(f"black : {state.black}, white : {state.white}")
        print("turn : ", "BLACK(1)" if state.turn else "WHITE(0)")
        possible_pos, TF = put_able(state)
        #  打てる手がなかったら、パスする
        if not TF:
            if end_check(state):
                show_winner(state)
            print("--- Pass ---")
            state.turn ^= 1
            continue

        if state.turn == BLACK:  # 人間のターン
            #  正しい打ちて以外は弾く
            while True:
                way = input()
                way = convert_user2num(way)
                if not way:
                    print("INVALID")
                    continue
                if way in possible_pos:
                    state = possible_pos[way]
                    break
        else:  # CPUのターン
            state, way = neg_max(state, 0, MIN_VAL, MAX_VAL)
            print(convert_way(way[0], way[1]))
        #  盤面の表示など
        board = copy.deepcopy(state.board)
        display(board)


main()
