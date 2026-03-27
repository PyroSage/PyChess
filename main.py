import pygame
import chess

# Constants
WIDTH, HEIGHT = 640, 640
SQ_SIZE = WIDTH // 8
LIGHT_SQAURE = "#eeeed2"
DARK_SQUARE = "#769656"
HIGHLIGHT_SQUARE = "#baca44"
CAPTURE_SQUARE = "#caa044"
CHECK_COLOR = "#ff5555"
BUTTON_RECT = pygame.Rect(WIDTH+10, 20, 100, 40) # Positioned to the right of the board

def draw_ui(screen, board):
    """Draws the 'Back' button and other UI elements."""
    # Draw Button Background
    pygame.draw.rect(screen, (50, 50, 50), BUTTON_RECT, border_radius=5)
    
    # Draw Text
    font = pygame.font.SysFont("Arial", 20, bold=True)
    text = font.render("BACK", True, (255, 255, 255))
    screen.blit(text, (BUTTON_RECT.x + 25, BUTTON_RECT.y + 10))

def handle_undo(board):
    """Pops the last two moves (Player + AI) or just one."""
    if len(board.move_stack) > 0:
        board.pop()

def highlight_pieces(screen, board, selected_square):
    """Handles all square overlays: Legal moves, captures, and check."""
    
    # 1. Highlight the King if in Check
    if board.is_check():
        king_sq = board.king(board.turn)
        r, c = 7 - chess.square_rank(king_sq), chess.square_file(king_sq)
        # We draw a soft red square under the king
        s = pygame.Surface((SQ_SIZE, SQ_SIZE))
        s.set_alpha(150) # Transparency
        s.fill(pygame.Color(CHECK_COLOR))
        screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))

    # 2. Highlight Legal Steps and Captures
    if selected_square is not None:
        # Get all legal moves for the selected piece
        legal_moves = board.legal_moves
        for move in legal_moves:
            if move.from_square == selected_square:
                r, c = 7 - chess.square_rank(move.to_square), chess.square_file(move.to_square)
                
                # Check if this move is a capture
                is_capture = board.piece_at(move.to_square) is not None
                
                # Draw the highlight
                s = pygame.Surface((SQ_SIZE, SQ_SIZE))
                s.set_alpha(180)
                
                if is_capture:
                    s.fill(pygame.Color(CAPTURE_SQUARE))
                else:
                    s.fill(pygame.Color(HIGHLIGHT_SQUARE))
                
                screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))

IMAGES = {}

def load_images():
    # Mapping python-chess symbols to your specific filenames
    # 'p' = black pawn, 'P' = white pawn, etc.
    pieces = {
        'p': 'black-pawn', 'r': 'black-rook', 'n': 'black-knight', 
        'b': 'black-bishop', 'q': 'black-queen', 'k': 'black-king',
        'P': 'white-pawn', 'R': 'white-rook', 'N': 'white-knight', 
        'B': 'white-bishop', 'Q': 'white-queen', 'K': 'white-king'
    }
    
    for symbol, file_name in pieces.items():
        # Load the image and scale it to fit your square size
        img = pygame.image.load(f"pieces-png/{file_name}.png") # Adjust path if needed
        IMAGES[symbol] = pygame.transform.scale(img, (SQ_SIZE, SQ_SIZE))
     
def get_square_under_mouse():
    mouse_pos = pygame.mouse.get_pos()
    x, y = mouse_pos
    col = x // SQ_SIZE
    row = y // SQ_SIZE
    # Flip the row because pygame (0,0) is top-left, 
    # but chess.SQUARE (0) is bottom-left (A1)
    return chess.square(col, 7 - row)
        
def draw_pieces(screen, board, selected_square, dragging_piece, mouse_pos):
    for sq in chess.SQUARES:
        # 1. Skip the piece that is currently being dragged 
        # (We will draw it last so it appears on top)
        if sq == selected_square:
            continue
            
        piece = board.piece_at(sq)
        if piece:
            # Convert chess square to (row, col)
            # Rank 0 is bottom, so we do 7 - rank for Pygame's top-down coords
            r = 7 - chess.square_rank(sq)
            c = chess.square_file(sq)
            
            # Draw the static piece
            screen.blit(IMAGES[piece.symbol()], (c * SQ_SIZE, r * SQ_SIZE))
    
    # 2. Draw the 'floating' piece at the mouse cursor
    if dragging_piece:
        img = IMAGES[dragging_piece.symbol()]
        # Center the piece on the cursor
        x = mouse_pos[0] - SQ_SIZE // 2
        y = mouse_pos[1] - SQ_SIZE // 2
        screen.blit(img, (x, y))

def draw_board(screen):
    colors = [pygame.Color(LIGHT_SQAURE), pygame.Color(DARK_SQUARE)]
    for r in range(8):
        for c in range(8):
            color = colors[((r + c) % 2)]
            pygame.draw.rect(screen, color, pygame.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH+120, HEIGHT))
    board = chess.Board()
    
    load_images()
    
    running = True
    selected_square = None
    dragging_piece = None

    while running:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if BUTTON_RECT.collidepoint(event.pos):
                    handle_undo(board)
                else:
                    sq = get_square_under_mouse()
                    piece = board.piece_at(sq)
                    if sq is not None:
                        piece = board.piece_at(sq)
                        if piece and piece.color == board.turn:
                            selected_square = sq
                            dragging_piece = piece
            elif event.type == pygame.MOUSEBUTTONUP:
                if selected_square is not None:
                    target_sq = get_square_under_mouse()
                    # Create the move object
                    move = chess.Move(selected_square, target_sq)
                    
                    # VALIDATION: Only push if the move is legal
                    if move in board.legal_moves:
                        board.push(move)
                    
                    # Reset state
                    selected_square = None
                    dragging_piece = None
            
            # Handle mouse clicks to select and move pieces here...

        screen.fill((0, 0, 0))
        draw_board(screen)
        highlight_pieces(screen, board, selected_square)
        draw_pieces(screen, board, selected_square, dragging_piece, mouse_pos)
        draw_ui(screen, board)
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()