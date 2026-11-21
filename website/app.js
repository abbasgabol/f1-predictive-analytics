import { portraits } from "./portraits.js";

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

function driverIdentity(driver, nameTag, lazy = false) {
  const identity = element("div", undefined, "driver-identity");
  const photo = element("img", undefined, "driver-photo");
  photo.alt = "";
  photo.width = 80;
  photo.height = 80;
  photo.decoding = "async";
  if (lazy) photo.loading = "lazy";
  const fallback = element("span", driver.code, "driver-photo-fallback");
  fallback.setAttribute("aria-hidden", "true");
  fallback.hidden = true;
  photo.addEventListener("error", () => {
    photo.hidden = true;
    fallback.hidden = false;
  });
  photo.src = portraits[driver.code];
  const label = element("div");
  label.append(element(nameTag, driver.name), element("small", driver.team));
  identity.append(photo, fallback, label);
  return identity;
}

function driverRow(code, index, drivers, actual) {
  const driver = drivers.get(code);
  const row = element("li", undefined, "podium-row");
  const identity = driverIdentity(driver, "strong");
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
    const identity = element("th");
    identity.scope = "row";
    identity.append(driverIdentity(driver, "span", true));
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

function renderProbabilities(race) {
  for (const key of ["podium", "win"]) {
    const ranked = [...race.field].sort((a, b) => b[key] - a[key]).slice(0, 6);
    const rows = ranked.map((driver) => {
      const row = element("li", undefined, "probability-row");
      const code = element("abbr", driver.code);
      code.title = driver.name;
      code.setAttribute("aria-label", driver.name);
      const track = element("span", undefined, "probability-track");
      const fill = element("span", undefined, "probability-fill");
      fill.style.width = percent(driver[key]);
      track.setAttribute("aria-hidden", "true");
      track.append(fill);
      row.append(code, track, element("span", percent(driver[key]), "probability-value"));
      return row;
    });
    byId(key + "-bars").replaceChildren(...rows);
  }
}

async function renderBacktest() {
  try {
    const response = await fetch("./backtest.json");
    if (!response.ok) return;
    const { folds, mean, winners } = await response.json();
    byId("backtest-bars").replaceChildren(...folds.map(({ round, hits }) => {
      const item = element("li", undefined, "backtest-column");
      const bar = element("span", undefined, "backtest-track");
      bar.setAttribute("aria-hidden", "true");
      const fill = element("span", undefined, "backtest-fill");
      fill.style.height = percent(hits / 3);
      bar.append(fill);
      const roundLabel = element("span", "R" + round, "backtest-round");
      roundLabel.setAttribute("aria-label", "Round " + round);
      const score = element("strong", hits + "/3", "backtest-score");
      item.append(roundLabel, score, bar);
      return item;
    }));
    byId("backtest-mean").textContent = mean.toFixed(2) + " / 3";
    byId("backtest-wins").textContent = winners + " / " + folds.length;
    byId("backtest-summary").hidden = false;
    byId("backtest-chart").hidden = false;
  } catch (error) {
    console.error(error);
  }
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
  renderProbabilities(race);
  renderGrid(race);
}

function renderScores(races) {
  const scored = races.filter((race) => race.actual);
  let hits = 0, baseline = 0, wins = 0, fullPodiums = 0;
  for (const race of scored) {
    const qualifying = race.field.filter((driver) => driver.qualifying <= 3)
      .map((driver) => driver.code);
    const correctNames = overlap(race.prediction, race.actual);
    hits += correctNames;
    baseline += overlap(qualifying, race.actual);
    wins += Number(race.prediction[0] === race.actual[0]);
    fullPodiums += Number(correctNames === race.actual.length);
  }
  byId("scored").textContent = scored.length + " of " + races.length + " races scored";
  const slots = scored.length * 3;
  const metrics = [
    [hits, slots, "Podium picks correct", "Driver appeared anywhere on the podium"],
    [baseline, slots, "Qualifying baseline", "Top three qualifiers on the podium"],
    [wins, scored.length, "Winners correct", "Predicted winner finished first"],
    [fullPodiums, scored.length, "All three names", "All picks made the podium, in any order"],
  ];
  byId("metrics").replaceChildren(...metrics.map(([value, total, label, note]) => {
    const tile = element("div", undefined, "metric");
    const number = element("div", String(value), "metric-value");
    number.append(element("span", " / " + total));
    const valueRow = element("div", undefined, "metric-result");
    valueRow.append(number, element("span", total ? percent(value / total) : "—", "metric-percent"));
    tile.append(element("h3", label), valueRow, element("p", note, "muted"));
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
    renderScores(races);
    selector.disabled = false;
    byId("race-detail").hidden = false;
  } catch (error) {
    byId("load-error").textContent = "Race data could not load. Refresh the page to try again.";
    byId("load-error").hidden = false;
    byId("scored").textContent = "Scores could not load.";
    console.error(error);
  }
}

init();
renderBacktest();
