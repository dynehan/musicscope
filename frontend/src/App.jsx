import { useEffect, useMemo, useState } from "react";
import { api } from "./api";
import {
  PieChart,
  Pie,
  Tooltip,
  Legend,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Cell,
} from "recharts";

export default function App() {
  const [country, setCountry] = useState("spain");
  const [compareCountry, setCompareCountry] = useState("united states");

  const [genreData, setGenreData] = useState(null);
  const [artistData, setArtistData] = useState(null);
  const [comparisonData, setComparisonData] = useState(null);

  const [error, setError] = useState("");

  // Admin ETL UI state
  const [etlLoading, setEtlLoading] = useState(false);
  const [etlMsg, setEtlMsg] = useState("");
  const [refreshKey, setRefreshKey] = useState(0);

  // Canonical values used for API/DB lookups should be lowercase.
  // Labels are what the user sees.
  const COUNTRY_OPTIONS = [
    { value: "spain", label: "Spain" },
    { value: "united states", label: "United States" },
    { value: "south korea", label: "South Korea" },
    { value: "mexico", label: "Mexico" },
  ];

  const normalizeCountry = (v) => String(v ?? "").trim().toLowerCase();

  const countryLabel = useMemo(() => {
    const v = normalizeCountry(country);
    return COUNTRY_OPTIONS.find((o) => o.value === v)?.label || country;
  }, [country]);

  const compareCountryLabel = useMemo(() => {
    const v = normalizeCountry(compareCountry);
    return COUNTRY_OPTIONS.find((o) => o.value === v)?.label || compareCountry;
  }, [compareCountry]);

  const c1 = useMemo(() => normalizeCountry(country), [country]);
  const c2 = useMemo(() => normalizeCountry(compareCountry), [compareCountry]);

  // ---- Theme (single-blue palette) ----
  const COLORS = {
    primary: "#2563EB",
    primaryLight: "#93C5FD",
    primaryLighter: "#DBEAFE",
    border: "#E5E7EB",
    text: "#0F172A",
    muted: "#64748B",
    bg: "#FFFFFF",
    cardBg: "#FFFFFF",
  };

  // Multiple shades of the same blue for pie slices
  const pieColors = [
    "#1D4ED8",
    "#2563EB",
    "#3B82F6",
    "#60A5FA",
    "#93C5FD",
    "#BFDBFE",
    "#DBEAFE",
    "#1E40AF",
    "#1E3A8A",
    "#0B3AA4",
  ];

  const styles = {
    page: {
      padding: 24,
      fontFamily: "system-ui, -apple-system, Segoe UI, Roboto, sans-serif",
      maxWidth: 1280,
      margin: "0 auto",
      color: COLORS.text,
    },
    title: {
      fontSize: 44,
      fontWeight: 800,
      letterSpacing: "-0.02em",
      margin: "6px 0 18px",
    },
    subRow: {
      display: "flex",
      justifyContent: "space-between",
      gap: 12,
      flexWrap: "wrap",
      alignItems: "center",
      marginBottom: 14,
    },
    meta: {
      color: COLORS.muted,
      fontSize: 14,
      margin: "6px 0 0",
    },
    toolbar: {
      border: `1px solid ${COLORS.border}`,
      borderRadius: 14,
      background: COLORS.cardBg,
      padding: 14,
      display: "flex",
      gap: 12,
      flexWrap: "wrap",
      alignItems: "center",
      marginBottom: 16,
      boxShadow: "0 1px 0 rgba(15, 23, 42, 0.04)",
    },
    label: {
      fontSize: 14,
      color: COLORS.muted,
      fontWeight: 600,
      display: "flex",
      gap: 8,
      alignItems: "center",
    },
    select: {
      appearance: "auto",
      border: `1px solid ${COLORS.border}`,
      borderRadius: 10,
      padding: "8px 10px",
      background: COLORS.bg,
      fontSize: 14,
      color: COLORS.text,
      outline: "none",
      minWidth: 180,
    },
    button: {
      border: `1px solid ${COLORS.primary}`,
      background: COLORS.primary,
      color: "white",
      padding: "9px 12px",
      borderRadius: 10,
      fontSize: 14,
      fontWeight: 700,
      cursor: "pointer",
    },
    buttonSecondary: {
      border: `1px solid ${COLORS.border}`,
      background: COLORS.primaryLighter,
      color: COLORS.primary,
      padding: "9px 12px",
      borderRadius: 10,
      fontSize: 14,
      fontWeight: 800,
      cursor: "pointer",
    },
    buttonDisabled: {
      opacity: 0.6,
      cursor: "not-allowed",
    },
    msgOk: { color: "#166534", fontWeight: 600, margin: "6px 0 12px" },
    msgErr: { color: "#B91C1C", fontWeight: 600, margin: "6px 0 12px" },

    grid: {
      display: "grid",
      gridTemplateColumns: "1fr 1fr",
      gap: 18,
      alignItems: "stretch",
    },
    card: {
      border: `1px solid ${COLORS.border}`,
      borderRadius: 14,
      background: COLORS.cardBg,
      padding: 16,
      boxShadow: "0 1px 0 rgba(15, 23, 42, 0.04)",
      minHeight: 520,
    },
    cardHeader: {
      display: "flex",
      justifyContent: "space-between",
      alignItems: "baseline",
      gap: 10,
      marginBottom: 10,
    },
    cardTitle: {
      fontSize: 18,
      fontWeight: 800,
      margin: 0,
      letterSpacing: "-0.01em",
    },
    helper: { color: COLORS.muted, fontSize: 13, margin: 0 },
    chartWrap: { height: 460 },
    fullCard: {
      marginTop: 18,
      border: `1px solid ${COLORS.border}`,
      borderRadius: 14,
      background: COLORS.cardBg,
      padding: 16,
      boxShadow: "0 1px 0 rgba(15, 23, 42, 0.04)",
    },
  };

  useEffect(() => {
    setError("");
    setGenreData(null);
    setArtistData(null);
    setComparisonData(null);

    const comparisonPromise =
      c2 === c1
        ? Promise.resolve({ data: null })
        : api.get("/analytics/country-genre-comparison", {
            params: { c1, c2, top_n: 10 },
          });

    Promise.all([
      api.get("/analytics/genre-distribution", { params: { country: c1, top_n: 10 } }),
      api.get("/analytics/top-artists-by-country", { params: { country: c1, top_n: 10 } }),
      comparisonPromise,
    ])
      .then(([gRes, aRes, cRes]) => {
        setGenreData(gRes.data);
        setArtistData(aRes.data);
        setComparisonData(cRes.data);
      })
      .catch((e) => setError(e?.response?.data?.detail || e.message));
  }, [country, compareCountry, refreshKey, c1, c2]);

  const pieData = useMemo(() => {
    if (!genreData?.genres) return [];
    return genreData.genres.map((g) => ({ name: g.genre, value: g.count }));
  }, [genreData]);

  const barData = useMemo(() => {
    if (!artistData?.artists) return [];
    return artistData.artists.map((a) => ({ name: a.artist_name, value: a.track_count }));
  }, [artistData]);

  const comparisonBarData = useMemo(() => {
    if (!comparisonData?.genres) return [];
    return comparisonData.genres.map((g) => ({
      genre: g.genre,
      c1_count: g.c1_count,
      c2_count: g.c2_count,
    }));
  }, [comparisonData]);

  // Admin ETL handlers
  const runLastfmETL = async () => {
    try {
      setEtlLoading(true);
      setEtlMsg("");
      await api.post("/etl/lastfm/run", null, { params: { country: c1, limit: 20 } });
      setEtlMsg(`Last.fm ETL done for ${countryLabel}. Refreshing charts...`);
      setRefreshKey((v) => v + 1);
    } catch (e) {
      setEtlMsg(e?.response?.data?.detail || e.message);
    } finally {
      setEtlLoading(false);
    }
  };

  const runMusicbrainzETL = async () => {
    try {
      setEtlLoading(true);
      setEtlMsg("");
      await api.post("/etl/musicbrainz/run", null, { params: { limit: 50 } });
      setEtlMsg("MusicBrainz ETL done. Refreshing charts...");
      setRefreshKey((v) => v + 1);
    } catch (e) {
      setEtlMsg(e?.response?.data?.detail || e.message);
    } finally {
      setEtlLoading(false);
    }
  };

  return (
    <div style={styles.page}>
      <div style={styles.subRow}>
        <h1 style={styles.title}>MusicScope</h1>
      </div>

      <div style={styles.toolbar}>
        <label style={styles.label}>
          Country
          <select style={styles.select} value={country} onChange={(e) => setCountry(e.target.value)}>
            {COUNTRY_OPTIONS.map((o) => (
              <option key={o.value} value={o.value}>
                {o.label}
              </option>
            ))}
          </select>
        </label>

        <button
          style={{ ...styles.button, ...(etlLoading ? styles.buttonDisabled : {}) }}
          onClick={runLastfmETL}
          disabled={etlLoading}
        >
          {etlLoading ? "Running..." : "Run Last.fm ETL"}
        </button>

        <button
          style={{ ...styles.buttonSecondary, ...(etlLoading ? styles.buttonDisabled : {}) }}
          onClick={runMusicbrainzETL}
          disabled={etlLoading}
        >
          {etlLoading ? "Running..." : "Run MusicBrainz ETL"}
        </button>

        {genreData && (
          <div style={{ marginLeft: "auto" }}>
            <p style={styles.meta}>
              Latest: <b>{genreData.latest_fetched_at}</b> · Tracks: <b>{genreData.total_tracks}</b> · Tags:{" "}
              <b>{genreData.total_genre_tags_counted}</b>
            </p>
          </div>
        )}
      </div>

      {etlMsg && <p style={etlMsg.includes("done") ? styles.msgOk : styles.msgErr}>{etlMsg}</p>}
      {error && <p style={styles.msgErr}>{error}</p>}
      {!genreData && !artistData && !error && <p style={styles.meta}>Loading…</p>}

      {(genreData || artistData) && (
        <>
          <div style={styles.grid}>
            {/* Pie Chart: Genres */}
            <div style={styles.card}>
              <div style={styles.cardHeader}>
                <h2 style={styles.cardTitle}>Top Genres</h2>
                <p style={styles.helper}>Based on MusicBrainz tags</p>
              </div>

              {pieData.length === 0 ? (
                <p style={styles.meta}>No genre data. Run ETL for this country.</p>
              ) : (
                <div style={styles.chartWrap}>
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie data={pieData} dataKey="value" nameKey="name" outerRadius={150}>
                        {pieData.map((_, i) => (
                          <Cell key={`cell-${i}`} fill={pieColors[i % pieColors.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              )}
            </div>

            {/* Bar Chart: Top Artists */}
            <div style={styles.card}>
              <div style={styles.cardHeader}>
                <h2 style={styles.cardTitle}>Top Artists</h2>
                <p style={styles.helper}>Count of tracks in Top N</p>
              </div>

              {barData.length === 0 ? (
                <p style={styles.meta}>No artist data. Run ETL for this country.</p>
              ) : (
                <div style={styles.chartWrap}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={barData} margin={{ top: 10, right: 10, left: 10, bottom: 72 }}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" interval={0} angle={-18} textAnchor="end" height={72} />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="value" fill={COLORS.primary} radius={[8, 8, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              )}
            </div>
          </div>

          {/* Country Comparison */}
          <div style={styles.fullCard}>
            <div style={{ ...styles.cardHeader, marginBottom: 8 }}>
              <h2 style={styles.cardTitle}>Country Comparison</h2>

              <label style={styles.label}>
                Compare with
                <select
                  style={styles.select}
                  value={compareCountry}
                  onChange={(e) => setCompareCountry(e.target.value)}
                >
                  {COUNTRY_OPTIONS.map((o) => (
                    <option key={o.value} value={o.value}>
                      {o.label}
                    </option>
                  ))}
                </select>
              </label>
            </div>

            <p style={styles.meta}>
              Comparing <b>{countryLabel}</b> vs <b>{compareCountryLabel}</b> (Top 10 genres)
            </p>

            {c2 === c1 ? (
              <p style={styles.meta}>Please choose a different country to compare.</p>
            ) : comparisonBarData.length === 0 ? (
              <p style={styles.meta}>No comparison data. Run ETL for both countries.</p>
            ) : (
              <div style={{ height: 520, marginTop: 6 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={comparisonBarData} margin={{ top: 10, right: 10, left: 10, bottom: 72 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="genre" interval={0} angle={-18} textAnchor="end" height={72} />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="c1_count" name={countryLabel} fill={COLORS.primary} radius={[8, 8, 0, 0]} />
                    <Bar
                      dataKey="c2_count"
                      name={compareCountryLabel}
                      fill={COLORS.primaryLight}
                      radius={[8, 8, 0, 0]}
                    />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
