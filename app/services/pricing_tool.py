import os
from amadeus import Client, ResponseError
from app.core.cache import cache_result

class PricingTool:
    def __init__(self):
        # Initialize Amadeus Client
        self.amadeus = Client(
            client_id=os.getenv("AMADEUS_CLIENT_ID"),
            client_secret=os.getenv("AMADEUS_CLIENT_SECRET")
        )

    @cache_result(ttl_seconds=14400) # Cache for 4 hours
    def search_flights(self, origin: str, destination: str, date: str) -> dict:
        """
        Fetches the cheapest flight price.
        Returns a Dict (which gets auto-serialized to JSON by our decorator).
        """
        try:
            response = self.amadeus.shopping.flight_offers_search.get(
                originLocationCode=origin,
                destinationLocationCode=destination,
                departureDate=date,
                adults=1,
                max=1  # We only need the cheapest one
            )

            # Case 1: API returns success but no flights found
            if not response.data:
                return {"error": "No flights found", "price": None}

            # Case 2: Success - Extract details
            offer = response.data[0]
            return {
                "price": offer['price']['total'],
                "currency": offer['price']['currency'],
                "carrier": offer['validatingAirlineCodes'][0],
                "origin": origin,
                "destination": destination
            }

        except ResponseError as error:
            # Case 3: API Error (Auth failed, Rate limit, etc.)
            print(f"Amadeus Error: {error}")
            return {"error": str(error), "price": None}
        except Exception as e:
            # Case 4: Generic Python Error
            print(f"Unexpected Error: {e}")
            return {"error": "Internal Tool Error", "details": str(e)}

# Initialize singleton
pricing_tool = PricingTool()

# Define the Tool Schema for the LLM
PRICING_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "get_flight_price",
        "description": "Get flight prices between two cities for a specific date.",
        "parameters": {
            "type": "object",
            "properties": {
                "origin": {"type": "string", "description": "3-letter IATA code (e.g. JFK)"},
                "destination": {"type": "string", "description": "3-letter IATA code (e.g. LHR)"},
                "date": {"type": "string", "description": "Date in YYYY-MM-DD format"},
            },
            "required": ["origin", "destination", "date"],
        },
    }
}