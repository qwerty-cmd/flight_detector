"""
LED display module for flight information.
Handles displaying flight data on RGB LED matrix.
"""
from typing import Dict, Any, List, Optional
from src.utils import Aircraft

# Try to import RGB matrix library (only available on Raspberry Pi)
try:
    from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
    RGB_MATRIX_AVAILABLE = True
except ImportError:
    RGB_MATRIX_AVAILABLE = False
    RGBMatrix = None
    RGBMatrixOptions = None
    graphics = None


class LEDDisplay:
    """LED matrix display controller."""

    # Country abbreviations mapping
    COUNTRY_ABBREV = {
        'United Kingdom': 'UK',
        'United States': 'USA',
        'Germany': 'DE',
        'France': 'FR',
        'Spain': 'ES',
        'Italy': 'IT',
        'Netherlands': 'NL',
        'Belgium': 'BE',
        'Switzerland': 'CH',
        'Austria': 'AT',
        'Canada': 'CA',
        'Australia': 'AU',
        'Japan': 'JP',
        'China': 'CN',
        'India': 'IN',
        'Brazil': 'BR',
    }

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize LED display.

        Args:
            config: Display configuration dictionary
        """
        self.config = config
        self.enabled = config.get('enabled', False)
        self.rotation_seconds = config.get('rotation_seconds', 8)
        self.matrix = None
        self.font = None
        self.aircraft_queue: List[Aircraft] = []
        self.queue_index = 0

        # Check if RGB matrix is available
        rgb_available = RGB_MATRIX_AVAILABLE or (RGBMatrix is not None)

        if self.enabled and rgb_available:
            self._init_matrix()
        elif self.enabled and not rgb_available:
            print("Warning: RGB Matrix library not available. Display disabled.")
            self.enabled = False

    def _init_matrix(self) -> None:
        """Initialize RGB matrix hardware."""
        options = RGBMatrixOptions()
        options.rows = self.config.get('led_rows', 32)
        options.cols = self.config.get('led_cols', 64)
        options.chain_length = self.config.get('led_chain', 1)
        options.parallel = self.config.get('led_parallel', 1)
        options.brightness = self.config.get('brightness', 80)

        self.matrix = RGBMatrix(options=options)

        # Load font if specified
        font_path = self.config.get('font_path')
        if font_path and graphics:
            self.font = graphics.Font()
            self.font.LoadFont(font_path)

    def abbreviate_country(self, country: str) -> str:
        """
        Abbreviate country name for display.

        Args:
            country: Full country name

        Returns:
            Abbreviated country name
        """
        return self.COUNTRY_ABBREV.get(country, country)

    def format_flight_info(self, aircraft: Aircraft) -> str:
        """
        Format flight information for display.

        Args:
            aircraft: Aircraft object

        Returns:
            Formatted string for display
        """
        # Get flight number or callsign
        flight_id = aircraft.flight_number or aircraft.callsign or aircraft.icao

        # Get origin and destination
        origin = aircraft.origin_country
        destination = aircraft.destination_country

        if origin and destination:
            origin_abbrev = self.abbreviate_country(origin)
            dest_abbrev = self.abbreviate_country(destination)
            return f"{flight_id}\n{origin_abbrev} -> {dest_abbrev}"
        elif origin:
            origin_abbrev = self.abbreviate_country(origin)
            return f"{flight_id}\nFrom {origin_abbrev}"
        else:
            return f"{flight_id}\nUnknown Route"

    def show_flight(self, aircraft: Aircraft) -> None:
        """
        Display flight information on LED matrix.

        Args:
            aircraft: Aircraft object to display
        """
        if not self.enabled:
            # Print to console for testing
            print(f"[Display] {self.format_flight_info(aircraft)}")
            return

        # Clear display
        self.matrix.Clear()

        # Format and display text
        text = self.format_flight_info(aircraft)
        lines = text.split('\n')

        # Display text (simplified - actual implementation would use graphics library)
        if self.font and graphics:
            canvas = self.matrix.CreateFrameCanvas()
            color = graphics.Color(255, 255, 255)  # White

            y_pos = 10
            for line in lines:
                graphics.DrawText(canvas, self.font, 2, y_pos, color, line)
                y_pos += 12

            self.matrix.SwapOnVSync(canvas)
        else:
            # Fallback if no font loaded
            print(f"[Display] {text}")

    def show_waiting_message(self) -> None:
        """Display waiting for aircraft message."""
        if not self.enabled:
            print("[Display] Waiting for aircraft...")
            return

        if self.matrix:
            self.matrix.Clear()

            if self.font and graphics:
                canvas = self.matrix.CreateFrameCanvas()
                color = graphics.Color(100, 100, 100)  # Gray
                graphics.DrawText(canvas, self.font, 2, 10, color, "Waiting...")
                self.matrix.SwapOnVSync(canvas)

    def clear(self) -> None:
        """Clear the display."""
        if not self.enabled:
            return

        if self.matrix:
            self.matrix.Clear()

    def update_queue(self, aircraft_list: List[Aircraft]) -> None:
        """
        Update the display queue with new aircraft list.

        Args:
            aircraft_list: List of aircraft to display
        """
        self.aircraft_queue = aircraft_list
        self.queue_index = 0

    def get_next_aircraft(self) -> Optional[Aircraft]:
        """
        Get next aircraft from display queue.

        Returns:
            Next aircraft to display, or None if queue is empty
        """
        if not self.aircraft_queue:
            return None

        aircraft = self.aircraft_queue[self.queue_index]
        self.queue_index = (self.queue_index + 1) % len(self.aircraft_queue)

        return aircraft
