const seasonSelect = document.getElementById("season");

function row([position, name, points, team]) {
  const entry = document.createElement("tr");
  entry.insertCell().textContent = position;
  const identity = document.createElement("th");
  identity.scope = "row";
  identity.textContent = name;
  if (team) {
    const affiliation = document.createElement("small");
    affiliation.textContent = team;
    identity.append(affiliation);
  }
  entry.append(identity);
  entry.insertCell().textContent = points;
  return entry;
}

async function showStandings() {
  try {
    const response = await fetch("./standings.json");
    if (!response.ok) throw new Error("Standings data unavailable");
    const standings = await response.json();
    const years = Object.keys(standings).reverse();
    const requested = new URLSearchParams(location.search).get("season");
    const initial = years.includes(requested) ? requested : years[0];

    function render(year) {
      const data = standings[year];
      document.getElementById("driver-standings").replaceChildren(...data.drivers.map(row));
      document.getElementById("constructor-standings").replaceChildren(...data.constructors.map(row));
      const source = "https://www.formula1.com/en/results/" + year;
      document.getElementById("driver-source").href = source + "/drivers";
      document.getElementById("constructor-source").href = source + "/team";
      document.querySelectorAll(".standings-scroll").forEach((panel) => { panel.scrollTop = 0; });
    }

    seasonSelect.replaceChildren(...years.map((year) => new Option(year, year)));
    seasonSelect.value = initial;
    render(initial);
    seasonSelect.addEventListener("change", () => {
      render(seasonSelect.value);
      const url = new URL(location.href);
      url.searchParams.set("season", seasonSelect.value);
      history.replaceState(null, "", url);
    });
    seasonSelect.disabled = false;
    document.getElementById("season-standings").hidden = false;
  } catch (error) {
    document.getElementById("standings-error").hidden = false;
    console.error(error);
  }
}

showStandings();
