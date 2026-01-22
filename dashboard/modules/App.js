import { e } from "./shortcuts.js";

export default function App() {
  const [eventData, setEventData] = React.useState(null);

  const urlParams = new URLSearchParams(window.location.search);
  const eventName = urlParams.get("event");
  const eventToken = urlParams.get("token");

  if (!eventData) {
    fetch("/event/data", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ name: eventName, token: eventToken }),
    })
      .then((response) => response.json())
      .then((json) => {
        setEventData(json.data);
      });
    return;
  }

  const rows = [];
  for (var player in eventData.players) {
    const playerData = eventData.players[player] || {};
    const wins = playerData.wins || 0;
    const losses = playerData.losses || 0;
    const draws = playerData.draws || 0;
    const forfeitWins = playerData.forfeit_wins || 0;
    const forfeitLosses = playerData.forfeit_losses || 0;
    const ongoing = playerData.ongoing || 0;

    rows.push(
      e(
        "tr",
        { key: player },
        e("td", null, player),
        e("td", null, wins + forfeitWins + " (" + forfeitWins + ")"),
        e("td", null, losses + forfeitLosses + " (" + forfeitLosses + ")"),
        e("td", null, draws),
        e("td", null, ongoing),
      ),
    );
  }

  return e(
    "div",
    null,
    e("h1", null, eventName),
    e(
      "table",
      { className: "table table-striped" },
      e(
        "caption",
        null,
        "(parentheses show how many forfeits are included in the total)",
      ),
      e(
        "thead",
        null,
        e(
          "tr",
          null,
          e("th", null, "player"),
          e("th", null, "wins"),
          e("th", null, "losses"),
          e("th", null, "draws"),
          e("th", null, "ongoing"),
        ),
      ),
      e("tbody", null, rows),
    ),
  );
}
