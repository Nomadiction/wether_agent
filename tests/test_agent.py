from src.agent.weather_agent_lc import WeatherAgentLC

def test_extract_city_simple():
    ag = WeatherAgentLC(session_id="test_sess")
    assert ag._extract_city("Погода в Berlin") == "Berlin"
    assert ag._extract_city("weather in Paris") == "Paris"
    assert ag._extract_city("London") == "London"
    assert ag._extract_city("Что по погоде?") == ""

def test_reply_format_hint():
    ag = WeatherAgentLC(session_id="test_sess")
    out = ag.ask("как дела?")
    assert "Format:" in out
