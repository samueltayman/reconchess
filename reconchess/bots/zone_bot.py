import random
import array
from reconchess import *
import os
import math

def flipped_move(move):
    def flipped(square):
        return chess.square(chess.square_file(square), 7 - chess.square_rank(square))

    return chess.Move(from_square=flipped(move.from_square), to_square=flipped(move.to_square),
                promotion=move.promotion, drop=move.drop)
        


class ZoneBot(Player):

    def handle_game_start(self, color: Color, board: chess.Board):
        self.board = board
        self.color = color
        self.my_piece_captured_square = None
        self.move_sequence = [chess.Move(chess.B1, chess.C3), chess.Move(chess.C3, chess.B5), chess.Move(chess.B5, chess.D6),
     chess.Move(chess.D6, chess.E8)]
        if color == chess.BLACK:
            self.move_sequence = list(map(flipped_move, self.move_sequence))
        
        self.turn_number = 1
        self.selected_move = List[chess.Move]
        self.king_location = self.board.king(self.color)

    def evaluate(self, move_actions: List[chess.Move]):
        # evaluate board state
        value = 0
        pieces = [1, 2, 2, 2, 40, 100]
        for square, piece in self.board.piece_map().items():
            if piece is not None:
                if piece.color != self.color:
                    if piece.piece_type is chess.PAWN:
                        value -= pieces[0]
                    if piece.piece_type is chess.ROOK:
                        value -= pieces[1]
                    if piece.piece_type is chess.KNIGHT:
                        value -= pieces[2]
                    if piece.piece_type is chess.BISHOP:
                        value -= pieces[3]
                    if piece.piece_type is chess.QUEEN:
                        value -= pieces[4]
                    if piece.piece_type is chess.KING:
                        value -= pieces[5]
                if piece.color == self.color:
                    if square > self.king_location + 7:
                        value -= 20
        return value

    def minimax(self, move_actions: List[chess.Move], isMax, depth, alpha, beta):
        #base case
        if depth == 0:
            return -self.evaluate(move_actions)
    
        if isMax:
            bestValue = -math.inf
            for move in move_actions:
                self.board.push(move)
                value = self.minimax(move_actions, False, depth - 1, alpha, beta)
                print("As Max", value)
                if value > bestValue:
                    bestValue = value
                    self.selected_move.insert(0, move)
                alpha = max(alpha, bestValue)
                if beta <= alpha:
                    break
                self.board.pop()
                return bestValue
        else:
            bestValue = math.inf
            for move in move_actions:
                self.board.push(move)
                value = self.minimax(move_actions, True, depth - 1, alpha, beta)
                print("As Min", value)
                if value < bestValue:
                    print("here")
                    bestValue = value
                    self.selected_move.insert(0, move)
                beta = min(beta, bestValue)
                if beta <= alpha:
                    break
                self.board.pop()
                return bestValue


    def handle_opponent_move_result(self, captured_my_piece: bool, capture_square: Optional[Square]):
        # if the opponent captured our piece, remove it from our board.
        self.my_piece_captured_square = capture_square
        if captured_my_piece:
            self.board.remove_piece_at(capture_square)

    def choose_sense(self, sense_actions: List[Square], move_actions: List[chess.Move], seconds_left: float) -> Square:
        # sensing strategy to be implemented:
        # first scan front line area for enemy movement
        # if no enemies moved in area, scan opposite side next turn
        # keep track of expected number of pieces in area
        # if missing a piece, swap sides again changing general range

        # if our piece was just captured, sense where it was captured
        if self.my_piece_captured_square:
            return self.my_piece_captured_square

        # otherwise, just randomly choose a sense action, but don't sense on a square where our pieces are located
        for square, piece in self.board.piece_map().items():
            if self.turn_number / 5 % 2 == 0:
                    if piece.color == self.color and piece.piece_type is chess.KING:
                            return sense_actions(0)
            if piece.color == self.color:
                sense_actions.remove(square)
        return random.choice(sense_actions)

    def handle_sense_result(self, sense_result: List[Tuple[Square, Optional[chess.Piece]]]):
        # add the pieces in the sense result to our board
        for square, piece in sense_result:
            self.board.set_piece_at(square, piece)

    def choose_move(self, move_actions: List[chess.Move], seconds_left: float) -> Optional[chess.Move]:
        #while len(self.move_sequence) > 0 and self.move_sequence[0] not in move_actions:
        #    self.move_sequence.pop(0)
        #if len(self.move_sequence) > 0:
        #        self.turn_number = self.turn_number + 1
        #        return self.move_sequence.pop(0)
        #else:
            self.selected_move = [random.choice(move_actions + [None])]
            self.minimax(move_actions, True, 10, -math.inf, math.inf)
            if self.board.king(self.color) is not None:
                self.king_location = self.board.king(self.color)
            return self.selected_move.pop()


    def handle_move_result(self, requested_move: Optional[chess.Move], taken_move: Optional[chess.Move],
                           captured_opponent_piece: bool, capture_square: Optional[Square]):
        # if a move was executed, apply it to our board
        if taken_move is not None:
            self.board.push(taken_move)

    def handle_game_end(self, winner_color: Optional[Color], win_reason: Optional[WinReason],
                        game_history: GameHistory):
        pass