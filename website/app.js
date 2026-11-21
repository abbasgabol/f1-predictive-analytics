const byId = (id) => document.getElementById(id);
const percent = (value) => new Intl.NumberFormat("en", {
  style: "percent", maximumFractionDigits: 1,
}).format(value);

function element(tag, text, className) {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  if (className) node.className = className;
  return node;
}

function overlap(lineup, actual) {
  return lineup.filter((code) => actual.includes(code)).length;
}

function driverRow(code, index, drivers, actual) {
  const driver = drivers.get(code);
  const row = element("li", undefined, "podium-row");
  const identity = element("div");
  identity.append(element("strong", driver.name), element("small", driver.team));
  row.append(element("span", "P" + (index + 1), "position"), identity);
  if (actual) {
    const result = actual.indexOf(code);
    const label = result === index ? "Exact place" : result >= 0 ? "Podium hit" : "Miss";
    row.append(element("span", label, result >= 0 ? "verdict hit" : "verdict"));
  } else {
    row.append(element("span", code, "driver-code"));
  }
  return row;
}

function renderGrid(race) {
  const key = byId("sort").value;
  const direction = key === "qualifying" ? 1 : -1;
  const field = [...race.field].sort((a, b) => direction * (a[key] - b[key]));
  byId("field-count").textContent = field.length + " drivers";
  byId("grid").replaceChildren(...field.map((driver) => {
    const row = element("tr");
    const identity = element("th", driver.name);
    identity.scope = "row";
    identity.append(element("small", driver.team));
    const podium = element("td", undefined, "chance");
    const bar = element("meter");
    bar.max = 1;
    bar.value = driver.podium;
    bar.setAttribute("aria-hidden", "true");
    podium.append(bar, element("span", percent(driver.podium)));
    row.append(identity, element("td", driver.qualifying), element("td", percent(driver.win)), podium);
    return row;
  }));
}

function renderRace(race) {
  const drivers = new Map(race.field.map((driver) => [driver.code, driver]));
  byId("round").textContent = "ROUND " + race.round;
  byId("event-name").textContent = race.name + " Grand Prix";
  byId("cutoff").textContent = race.cutoff;
  byId("forecast").replaceChildren(...race.prediction.map((code, i) => driverRow(code, i, drivers, race.actual)));
  byId("actual").replaceChildren(...(race.actual ?? []).map((code, i) => driverRow(code, i, drivers)));
  byId("joint").textContent = percent(race.joint) + " model probability for this exact order";
  byId("result-note").textContent = race.source ?? "This archive does not include a race classification for Las Vegas.";
  byId("race-score").textContent = race.actual
    ? overlap(race.prediction, race.actual) + " / 3 podium picks"
    : "Awaiting result in archive";
  renderGrid(race);
}

function renderScores(races, selectRace) {
  const scored = races.filter((race) => race.actual);
  let hits = 0, baseline = 0, wins = 0, exact = 0;
  byId("scores").replaceChildren(...races.map((race) => {
    const row = element("tr");
    const title = element("th");
    title.scope = "row";
    const link = element("a", race.name);
    link.href = "?race=" + race.slug + "#explorer";
    link.addEventListener("click", (event) => {
      if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      selectRace(race.slug);
      byId("explorer").scrollIntoView();
      byId("race").focus({preventScroll: true});
    });
    title.append(link);
    row.append(title);
    if (!race.actual) {
      const cell = element("td", "Result absent from archive", "muted");
      cell.colSpan = 3;
      row.append(cell);
      return row;
    }
    const count = overlap(race.prediction, race.actual);
    const qualifying = [...race.field].sort((a, b) => a.qualifying - b.qualifying)
      .slice(0, 3).map((driver) => driver.code);
    const reference = overlap(qualifying, race.actual);
    const winner = race.prediction[0] === race.actual[0];
    hits += count;
    baseline += reference;
    wins += Number(winner);
    exact += Number(race.prediction.every((code, i) => code === race.actual[i]));
    row.append(element("td", count + " / 3"), element("td", reference + " / 3"), element("td", winner ? "Correct" : "Miss", winner ? "hit-text" : ""));
    return row;
  }));
  byId("scored").textContent = scored.length + " of " + races.length + " races scored";
  const slots = scored.length * 3;
  const metrics = [
    [hits, slots, "Podium names", "Order ignored"],
    [baseline, slots, "Qualifying baseline", "Order ignored"],
    [wins, scored.length, "Winners", "Correct first place"],
    [exact, scored.length, "Exact podiums", "All three in order"],
  ];
  byId("metrics").replaceChildren(...metrics.map(([value, total, label, note]) => {
    const tile = element("div", undefined, "metric");
    const number = element("div", String(value), "metric-value");
    number.append(element("span", " / " + total));
    tile.append(element("h3", label), number, element("p", note, "muted"));
    return tile;
  }));
}

async function init() {
  try {
    const response = await fetch("./races.json");
    if (!response.ok) throw new Error("Race data unavailable");
    const races = await response.json();
    const selector = byId("race");
    const lookup = new Map(races.map((race) => [race.slug, race]));
    selector.replaceChildren(...[...races].reverse().map((race) => new Option(race.name + " · R" + race.round, race.slug)));
    function selectRace(slug, updateUrl = true) {
      const race = lookup.get(slug) ?? [...races].reverse().find((entry) => entry.actual) ?? races.at(-1);
      selector.value = race.slug;
      renderRace(race);
      if (updateUrl) {
        const url = new URL(location.href);
        url.searchParams.set("race", race.slug);
        history.replaceState(null, "", url);
      }
    }
    selector.addEventListener("change", () => selectRace(selector.value));
    byId("sort").addEventListener("change", () => renderGrid(lookup.get(selector.value)));
    selectRace(new URLSearchParams(location.search).get("race"), false);
    renderScores(races, selectRace);
    selector.disabled = false;
    byId("race-detail").hidden = false;
  } catch (error) {
    byId("load-error").textContent = "Race data could not load. Refresh the page to try again.";
    byId("load-error").hidden = false;
    console.error(error);
  }
}

init();
