"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  ClipboardCheck,
  LogIn,
  LogOut,
  BarChart3,
  Radio,
  History,
  Pause,
  Play,
  WifiOff,
  Fingerprint,
  Trash2,
  ArrowUp,
  Copy,
} from "lucide-react";
import { staggerContainer, staggerItem, fadeInUp } from "@/lib/animations/framer-motion";
import { useAuthStore } from "@/lib/store/authStore";
import {
  listAttendance,
  getAttendanceStats,
  type AttendanceEvent,
  type AttendanceStats,
  type AttendanceListParams,
  type EventType,
} from "@/lib/api/attendance";
import { useAttendanceWebSocket } from "@/lib/hooks/useAttendanceWebSocket";

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

/** Maximum events to keep in the live feed before auto-trimming oldest. */
const MAX_LIVE_EVENTS = 100;

// ---------------------------------------------------------------------------
// Stat Card
// ---------------------------------------------------------------------------

function StatCard({
  label,
  value,
  icon: Icon,
  colorClass,
  hint,
}: {
  label: string;
  value: number | string;
  icon: React.ElementType;
  colorClass: string;
  hint?: string;
}) {
  return (
    <motion.div
      variants={staggerItem}
      className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-xl shadow-lg border border-gray-200/50 dark:border-gray-700/50 p-5"
    >
      <div className="flex items-center gap-4">
        <div className={`p-3 rounded-lg ${colorClass}`}>
          <Icon className="size-5" />
        </div>
        <div>
          <p className="text-2xl font-bold text-gray-900 dark:text-gray-100 tabular-nums">
            {value}
          </p>
          <p className="text-sm text-gray-500 dark:text-gray-400">{label}</p>
          {hint && (
            <p className="text-xs text-gray-400 dark:text-gray-500 mt-0.5">{hint}</p>
          )}
        </div>
      </div>
    </motion.div>
  );
}

// ---------------------------------------------------------------------------
// Event Type Badge
// ---------------------------------------------------------------------------

function EventBadge({ type }: { type: EventType }) {
  const config: Record<string, { bg: string; text: string; label: string }> = {
    IN: {
      bg: "bg-green-100 dark:bg-green-900/50",
      text: "text-green-700 dark:text-green-300",
      label: "IN",
    },
    OUT: {
      bg: "bg-amber-100 dark:bg-amber-900/50",
      text: "text-amber-700 dark:text-amber-300",
      label: "OUT",
    },
    DUPLICATE: {
      bg: "bg-purple-100 dark:bg-purple-900/50",
      text: "text-purple-600 dark:text-purple-300",
      label: "DUPLICATE",
    },
    UNKNOWN: {
      bg: "bg-gray-100 dark:bg-gray-700/50",
      text: "text-gray-600 dark:text-gray-400",
      label: "UNKNOWN",
    },
  };

  const c = config[type] ?? config.UNKNOWN;

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold ${c.bg} ${c.text}`}
    >
      {c.label}
    </span>
  );
}

// ---------------------------------------------------------------------------
// Live Scan Row — a single fingerprint scan in the live feed
// ---------------------------------------------------------------------------

function LiveScanRow({ event }: { event: AttendanceEvent }) {
  const borderColor: Record<string, string> = {
    IN: "border-l-green-500",
    OUT: "border-l-amber-500",
    DUPLICATE: "border-l-purple-400",
    UNKNOWN: "border-l-gray-400",
  };

  const time = new Date(event.occurred_at).toLocaleTimeString("en-KE", {
    hour: "numeric",
    minute: "2-digit",
    second: "2-digit",
    hour12: true,
  });

  const isDuplicate = event.event_type === "DUPLICATE";

  return (
    <motion.div
      layout
      initial={{ opacity: 0, x: -20, scale: 0.95 }}
      animate={{ opacity: isDuplicate ? 0.65 : 1, x: 0, scale: 1 }}
      exit={{ opacity: 0, height: 0, marginBottom: 0, scale: 0.9 }}
      transition={{ duration: 0.25, ease: "easeOut" }}
      className={`flex items-center gap-3 px-4 py-3 border-l-[3px] ${
        borderColor[event.event_type] ?? borderColor.UNKNOWN
      } bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-r-lg ${
        isDuplicate ? "opacity-65" : ""
      }`}
    >
      {/* Icon */}
      <div className="flex-shrink-0">
        {isDuplicate ? (
          <Copy className="size-4 text-purple-400" />
        ) : (
          <Fingerprint className="size-4 text-blue-500 dark:text-blue-400" />
        )}
      </div>

      {/* Badge */}
      <EventBadge type={event.event_type} />

      {/* Student info */}
      <div className="flex-1 min-w-0">
        <p className="font-medium text-gray-900 dark:text-gray-100 truncate text-sm">
          {event.student_name ?? "Unknown Student"}
          {event.admission_number && (
            <span className="ml-2 text-xs text-gray-500 dark:text-gray-400">
              ({event.admission_number})
            </span>
          )}
        </p>
        <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
          {event.device_name}
          {event.class_name && <span> · {event.class_name}</span>}
          {isDuplicate && (
            <span className="ml-1 italic text-purple-500 dark:text-purple-400">
              — duplicate tap
            </span>
          )}
        </p>
      </div>

      {/* Timestamp */}
      <p className="text-xs font-medium text-gray-500 dark:text-gray-400 tabular-nums whitespace-nowrap">
        {time}
      </p>
    </motion.div>
  );
}

// ---------------------------------------------------------------------------
// Live Capture Feed
// ---------------------------------------------------------------------------

function LiveCaptureFeed({
  events,
  isConnected,
  isPaused,
  onTogglePause,
  onClear,
  totalSeen,
}: {
  events: AttendanceEvent[];
  isConnected: boolean;
  isPaused: boolean;
  onTogglePause: () => void;
  onClear: () => void;
  totalSeen: number;
}) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const isAtTopRef = useRef(true);

  // Track whether user has scrolled away from top
  const handleScroll = useCallback(() => {
    if (scrollRef.current) {
      isAtTopRef.current = scrollRef.current.scrollTop < 20;
    }
  }, []);

  // Auto-scroll to top when new events arrive (newest first)
  useEffect(() => {
    if (!isPaused && isAtTopRef.current && scrollRef.current) {
      scrollRef.current.scrollTo({ top: 0, behavior: "smooth" });
    }
  }, [events.length, isPaused]);

  const scrollToTop = () => {
    scrollRef.current?.scrollTo({ top: 0, behavior: "smooth" });
  };

  return (
    <motion.div
      variants={fadeInUp}
      initial="hidden"
      animate="visible"
      className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-xl shadow-lg border border-gray-200/50 dark:border-gray-700/50"
    >
      {/* Header */}
      <div className="flex items-center justify-between px-5 py-4 border-b border-gray-200/50 dark:border-gray-700/50">
        <div className="flex items-center gap-3">
          <h3 className="font-semibold text-gray-900 dark:text-gray-100">
            Live Capture
          </h3>
          {isConnected ? (
            <span className="flex items-center gap-1.5 text-xs text-green-600 dark:text-green-400">
              <span className="relative flex size-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-500 opacity-75" />
                <span className="relative inline-flex rounded-full size-2 bg-green-500" />
              </span>
              Live
            </span>
          ) : (
            <span className="flex items-center gap-1.5 text-xs text-amber-600 dark:text-amber-400">
              <WifiOff className="size-3" />
              Reconnecting…
            </span>
          )}
          {events.length > 0 && (
            <span className="text-xs text-gray-400 dark:text-gray-500 tabular-nums">
              {events.length} shown · {totalSeen} total scans
            </span>
          )}
        </div>

        <div className="flex items-center gap-2">
          {events.length > 0 && (
            <button
              onClick={onClear}
              title="Clear feed"
              className="p-1.5 text-gray-400 hover:text-red-500 dark:text-gray-500 dark:hover:text-red-400 transition-colors rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700/50"
            >
              <Trash2 className="size-4" />
            </button>
          )}
          <button
            onClick={onTogglePause}
            className="flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors px-2.5 py-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700/50"
          >
            {isPaused ? <Play className="size-4" /> : <Pause className="size-4" />}
            {isPaused ? "Resume" : "Pause"}
          </button>
        </div>
      </div>

      {/* Paused banner */}
      {isPaused && (
        <div className="px-5 py-2 bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300 text-sm flex items-center gap-2">
          <Pause className="size-4" />
          Feed paused — new scans will appear when resumed
        </div>
      )}

      {/* Disconnected banner */}
      {!isConnected && (
        <div className="px-5 py-2 bg-amber-50 dark:bg-amber-900/20 text-amber-700 dark:text-amber-300 text-sm flex items-center gap-2">
          <WifiOff className="size-4" />
          Connection lost. Attempting to reconnect…
        </div>
      )}

      {/* Scan list */}
      <div
        ref={scrollRef}
        onScroll={handleScroll}
        className="max-h-[540px] overflow-y-auto p-3 space-y-1.5 scroll-smooth"
      >
        {events.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 text-gray-400 dark:text-gray-500">
            <Fingerprint className="size-12 mb-3 opacity-40" />
            <p className="font-medium">Waiting for fingerprint scans…</p>
            <p className="text-sm mt-1">
              Every scan will appear here instantly as students place their
              fingers on any connected device.
            </p>
          </div>
        ) : (
          <AnimatePresence initial={false} mode="popLayout">
            {events.map((evt) => (
              <LiveScanRow key={evt.id} event={evt} />
            ))}
          </AnimatePresence>
        )}
      </div>

      {/* Scroll to top button */}
      {events.length > 10 && (
        <div className="flex justify-center py-2 border-t border-gray-200/50 dark:border-gray-700/50">
          <button
            onClick={scrollToTop}
            className="flex items-center gap-1 text-xs text-gray-400 hover:text-blue-500 dark:text-gray-500 dark:hover:text-blue-400 transition-colors"
          >
            <ArrowUp className="size-3" />
            Scroll to latest
          </button>
        </div>
      )}
    </motion.div>
  );
}

// ---------------------------------------------------------------------------
// History Tab
// ---------------------------------------------------------------------------

function HistoryTab({
  events,
  total,
  page,
  totalPages,
  isLoading,
  onPageChange,
}: {
  events: AttendanceEvent[];
  total: number;
  page: number;
  totalPages: number;
  isLoading: boolean;
  onPageChange: (p: number) => void;
}) {
  return (
    <motion.div
      variants={fadeInUp}
      initial="hidden"
      animate="visible"
      className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-xl shadow-lg border border-gray-200/50 dark:border-gray-700/50"
    >
      {/* Summary */}
      <div className="px-5 py-4 border-b border-gray-200/50 dark:border-gray-700/50">
        <p className="text-sm text-gray-500 dark:text-gray-400">
          {total} record{total !== 1 ? "s" : ""} found
        </p>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-gray-500 dark:text-gray-400 border-b border-gray-200/50 dark:border-gray-700/50">
              <th className="px-5 py-3 font-medium">Time</th>
              <th className="px-5 py-3 font-medium">Student</th>
              <th className="px-5 py-3 font-medium hidden sm:table-cell">Admission #</th>
              <th className="px-5 py-3 font-medium hidden md:table-cell">Class</th>
              <th className="px-5 py-3 font-medium hidden md:table-cell">Device</th>
              <th className="px-5 py-3 font-medium">Type</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100 dark:divide-gray-700/50">
            {isLoading ? (
              Array.from({ length: 5 }).map((_, i) => (
                <tr key={i} className="animate-pulse">
                  <td className="px-5 py-3"><div className="h-4 w-20 bg-gray-200 dark:bg-gray-700 rounded" /></td>
                  <td className="px-5 py-3"><div className="h-4 w-32 bg-gray-200 dark:bg-gray-700 rounded" /></td>
                  <td className="px-5 py-3 hidden sm:table-cell"><div className="h-4 w-24 bg-gray-200 dark:bg-gray-700 rounded" /></td>
                  <td className="px-5 py-3 hidden md:table-cell"><div className="h-4 w-20 bg-gray-200 dark:bg-gray-700 rounded" /></td>
                  <td className="px-5 py-3 hidden md:table-cell"><div className="h-4 w-24 bg-gray-200 dark:bg-gray-700 rounded" /></td>
                  <td className="px-5 py-3"><div className="h-4 w-10 bg-gray-200 dark:bg-gray-700 rounded" /></td>
                </tr>
              ))
            ) : events.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-5 py-12 text-center text-gray-400 dark:text-gray-500">
                  No attendance records found for the selected filters.
                </td>
              </tr>
            ) : (
              events.map((evt) => {
                const time = new Date(evt.occurred_at).toLocaleTimeString("en-KE", {
                  hour: "numeric",
                  minute: "2-digit",
                  hour12: true,
                });
                return (
                  <tr
                    key={evt.id}
                    className="hover:bg-gray-50/50 dark:hover:bg-gray-700/30 transition-colors"
                  >
                    <td className="px-5 py-3 text-gray-900 dark:text-gray-100 tabular-nums">{time}</td>
                    <td className="px-5 py-3 font-medium text-gray-900 dark:text-gray-100">
                      {evt.student_name ?? "Unknown"}
                    </td>
                    <td className="px-5 py-3 text-gray-500 dark:text-gray-400 hidden sm:table-cell">
                      {evt.admission_number ?? "—"}
                    </td>
                    <td className="px-5 py-3 text-gray-500 dark:text-gray-400 hidden md:table-cell">
                      {evt.class_name ?? "—"}
                    </td>
                    <td className="px-5 py-3 text-gray-500 dark:text-gray-400 hidden md:table-cell">
                      {evt.device_name}
                    </td>
                    <td className="px-5 py-3">
                      <EventBadge type={evt.event_type} />
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between px-5 py-3 border-t border-gray-200/50 dark:border-gray-700/50">
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Page {page} of {totalPages}
          </p>
          <div className="flex gap-2">
            <button
              disabled={page <= 1}
              onClick={() => onPageChange(page - 1)}
              className="px-3 py-1 text-sm rounded-lg border border-gray-300 dark:border-gray-600 disabled:opacity-40 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            >
              Previous
            </button>
            <button
              disabled={page >= totalPages}
              onClick={() => onPageChange(page + 1)}
              className="px-3 py-1 text-sm rounded-lg border border-gray-300 dark:border-gray-600 disabled:opacity-40 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </motion.div>
  );
}

// ---------------------------------------------------------------------------
// Main Page
// ---------------------------------------------------------------------------

export default function AttendancePage() {
  const { token } = useAuthStore();

  // --- Tabs ---
  const [activeTab, setActiveTab] = useState<"live" | "history">("live");

  // --- Stats ---
  const [stats, setStats] = useState<AttendanceStats | null>(null);
  const [statsUpdatedAt, setStatsUpdatedAt] = useState<string | null>(null);

  // --- Live feed (purely WebSocket-driven) ---
  const [liveEvents, setLiveEvents] = useState<AttendanceEvent[]>([]);
  const [isPaused, setIsPaused] = useState(false);
  const [totalSeen, setTotalSeen] = useState(0);
  const [liveCounters, setLiveCounters] = useState({
    in: 0,
    out: 0,
    duplicate: 0,
    unknown: 0,
  });
  const [lastScanAt, setLastScanAt] = useState<string | null>(null);
  const seenIdsRef = useRef(new Set<string | number>());
  const pauseBufferRef = useRef<AttendanceEvent[]>([]);

  // --- History ---
  const [historyEvents, setHistoryEvents] = useState<AttendanceEvent[]>([]);
  const [historyTotal, setHistoryTotal] = useState(0);
  const [historyPage, setHistoryPage] = useState(1);
  const [historyTotalPages, setHistoryTotalPages] = useState(0);
  const [historyLoading, setHistoryLoading] = useState(false);

  // ---------------------------------------------------------------
  // Fetch stats
  // ---------------------------------------------------------------
  const fetchStats = useCallback(async () => {
    if (!token) return;
    try {
      const data = await getAttendanceStats(token);
      setStats(data);
      setStatsUpdatedAt(new Date().toISOString());
    } catch (err) {
      console.error("Failed to fetch attendance stats:", err);
    }
  }, [token]);

  useEffect(() => {
    if (token) fetchStats();
  }, [token, fetchStats]);

  // ---------------------------------------------------------------
  // WebSocket — always connected regardless of active tab
  // ---------------------------------------------------------------
  const handleWsEvents = useCallback(
    (incoming: AttendanceEvent[]) => {
      // Deduplicate by ID
      const newEvents = incoming.filter((e) => !seenIdsRef.current.has(e.id));
      if (newEvents.length === 0) return;

      for (const e of newEvents) seenIdsRef.current.add(e.id);
      setTotalSeen((prev) => prev + newEvents.length);

      let inDelta = 0;
      let outDelta = 0;
      let duplicateDelta = 0;
      let unknownDelta = 0;
      let latestOccurredAt: string | null = null;
      for (const e of newEvents) {
        if (!latestOccurredAt || new Date(e.occurred_at) > new Date(latestOccurredAt)) {
          latestOccurredAt = e.occurred_at;
        }
        if (e.event_type === "IN") inDelta += 1;
        else if (e.event_type === "OUT") outDelta += 1;
        else if (e.event_type === "DUPLICATE") duplicateDelta += 1;
        else unknownDelta += 1;
      }
      setLiveCounters((prev) => ({
        in: prev.in + inDelta,
        out: prev.out + outDelta,
        duplicate: prev.duplicate + duplicateDelta,
        unknown: prev.unknown + unknownDelta,
      }));
      if (latestOccurredAt) setLastScanAt(latestOccurredAt);

      const newestFirst = [...newEvents].reverse();

      if (isPaused) {
        // Buffer events while paused — they'll be prepended on resume
        pauseBufferRef.current = [
          ...newestFirst,
          ...pauseBufferRef.current,
        ].slice(0, MAX_LIVE_EVENTS);
      } else {
        // Prepend newest events, auto-trim oldest
        setLiveEvents((prev) =>
          [...newestFirst, ...prev].slice(0, MAX_LIVE_EVENTS)
        );
      }

      // Refresh stats on new scans
      fetchStats();
    },
    [isPaused, fetchStats]
  );

  const { isConnected } = useAttendanceWebSocket({
    onEvents: handleWsEvents,
    enabled: true, // Always connected
  });

  // Flush buffer when unpaused
  useEffect(() => {
    if (!isPaused && pauseBufferRef.current.length > 0) {
      const buffered = pauseBufferRef.current;
      pauseBufferRef.current = [];
      setLiveEvents((prev) =>
        [...buffered, ...prev].slice(0, MAX_LIVE_EVENTS)
      );
    }
  }, [isPaused]);

  // Clear live feed
  const handleClear = useCallback(() => {
    setLiveEvents([]);
    setTotalSeen(0);
    setLiveCounters({ in: 0, out: 0, duplicate: 0, unknown: 0 });
    setLastScanAt(null);
    seenIdsRef.current.clear();
    pauseBufferRef.current = [];
  }, []);

  // ---------------------------------------------------------------
  // Fetch history
  // ---------------------------------------------------------------
  const fetchHistory = useCallback(
    async (page: number) => {
      if (!token) return;
      setHistoryLoading(true);
      try {
        const res = await listAttendance(token, { page, page_size: 50 });
        setHistoryEvents(res.items);
        setHistoryTotal(res.total);
        setHistoryPage(res.page);
        setHistoryTotalPages(res.total_pages);
      } catch (err) {
        console.error("Failed to fetch history:", err);
      } finally {
        setHistoryLoading(false);
      }
    },
    [token]
  );

  useEffect(() => {
    if (activeTab === "history" && token) {
      fetchHistory(1);
    }
  }, [activeTab, token, fetchHistory]);

  // ---------------------------------------------------------------
  // Render
  // ---------------------------------------------------------------

  const statCards = [
    {
      label: "Total Events",
      value: stats?.total_events ?? 0,
      icon: ClipboardCheck,
      colorClass: "bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400",
      hint: "Stored attendance records",
    },
    {
      label: "Checked In",
      value: stats?.checked_in ?? 0,
      icon: LogIn,
      colorClass: "bg-green-100 text-green-600 dark:bg-green-900/30 dark:text-green-400",
      hint: "Classified as IN",
    },
    {
      label: "Checked Out",
      value: stats?.checked_out ?? 0,
      icon: LogOut,
      colorClass: "bg-amber-100 text-amber-600 dark:bg-amber-900/30 dark:text-amber-400",
      hint: "Classified as OUT",
    },
    {
      label: "Present Rate",
      value: stats ? `${stats.present_rate}%` : "—",
      icon: BarChart3,
      colorClass: "bg-indigo-100 text-indigo-600 dark:bg-indigo-900/30 dark:text-indigo-400",
      hint: "Based on daily attendance",
    },
  ];

  return (
    <motion.main
      initial={{ opacity: 0, scale: 0.98 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.4, ease: "easeOut" }}
      className="flex-1 space-y-6 p-4 sm:p-6 lg:p-8"
    >
      {/* Header */}
      <motion.div variants={fadeInUp} initial="hidden" animate="visible">
        <h1 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600">
          Attendance
        </h1>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
          Monitor student attendance in real-time
        </p>
      </motion.div>

      {/* Stats */}
      <motion.div
        variants={staggerContainer}
        initial="hidden"
        animate="visible"
        className="grid grid-cols-2 gap-4 lg:grid-cols-4"
      >
        {statCards.map((s) => (
          <StatCard key={s.label} {...s} />
        ))}
      </motion.div>

      <motion.div
        variants={fadeInUp}
        initial="hidden"
        animate="visible"
        className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-xl shadow-lg border border-gray-200/50 dark:border-gray-700/50 p-4 sm:p-5"
      >
        <div className="flex items-center justify-between gap-3 mb-3">
          <h2 className="text-sm font-semibold text-gray-700 dark:text-gray-300">
            Live Scan Statistics
          </h2>
          <p className="text-xs text-gray-500 dark:text-gray-400">
            Last scan:{" "}
            <span className="font-medium tabular-nums">
              {lastScanAt
                ? new Date(lastScanAt).toLocaleTimeString("en-KE", {
                    hour: "numeric",
                    minute: "2-digit",
                    second: "2-digit",
                    hour12: true,
                  })
                : "—"}
            </span>
            {"  •  "}
            Stats refreshed:{" "}
            <span className="font-medium tabular-nums">
              {statsUpdatedAt
                ? new Date(statsUpdatedAt).toLocaleTimeString("en-KE", {
                    hour: "numeric",
                    minute: "2-digit",
                    second: "2-digit",
                    hour12: true,
                  })
                : "—"}
            </span>
          </p>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
          <div className="rounded-lg bg-blue-50 dark:bg-blue-900/20 px-3 py-2">
            <p className="text-xs text-blue-700 dark:text-blue-300">Live Scans</p>
            <p className="text-lg font-semibold text-blue-700 dark:text-blue-300 tabular-nums">
              {totalSeen}
            </p>
          </div>
          <div className="rounded-lg bg-green-50 dark:bg-green-900/20 px-3 py-2">
            <p className="text-xs text-green-700 dark:text-green-300">IN</p>
            <p className="text-lg font-semibold text-green-700 dark:text-green-300 tabular-nums">
              {liveCounters.in}
            </p>
          </div>
          <div className="rounded-lg bg-amber-50 dark:bg-amber-900/20 px-3 py-2">
            <p className="text-xs text-amber-700 dark:text-amber-300">OUT</p>
            <p className="text-lg font-semibold text-amber-700 dark:text-amber-300 tabular-nums">
              {liveCounters.out}
            </p>
          </div>
          <div className="rounded-lg bg-purple-50 dark:bg-purple-900/20 px-3 py-2">
            <p className="text-xs text-purple-700 dark:text-purple-300">Duplicates</p>
            <p className="text-lg font-semibold text-purple-700 dark:text-purple-300 tabular-nums">
              {liveCounters.duplicate}
            </p>
          </div>
          <div className="rounded-lg bg-gray-100 dark:bg-gray-700/40 px-3 py-2">
            <p className="text-xs text-gray-600 dark:text-gray-300">Unknown</p>
            <p className="text-lg font-semibold text-gray-700 dark:text-gray-200 tabular-nums">
              {liveCounters.unknown}
            </p>
          </div>
        </div>
      </motion.div>

      {/* Tabs */}
      <div className="flex gap-6 border-b border-gray-200 dark:border-gray-700">
        <button
          onClick={() => setActiveTab("live")}
          className={`pb-3 text-sm font-medium transition-colors relative ${
            activeTab === "live"
              ? "text-blue-600 dark:text-blue-400"
              : "text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300"
          }`}
        >
          <span className="flex items-center gap-2">
            <Radio className="size-4" />
            Live Capture
            {liveEvents.length > 0 && activeTab !== "live" && (
              <span className="flex size-2">
                <span className="animate-ping absolute inline-flex h-2 w-2 rounded-full bg-green-500 opacity-75" />
                <span className="relative inline-flex rounded-full size-2 bg-green-500" />
              </span>
            )}
          </span>
          {activeTab === "live" && (
            <motion.div
              layoutId="tab-indicator"
              className="absolute bottom-0 left-0 right-0 h-0.5 bg-blue-600 dark:bg-blue-400 rounded-full"
            />
          )}
        </button>
        <button
          onClick={() => setActiveTab("history")}
          className={`pb-3 text-sm font-medium transition-colors relative ${
            activeTab === "history"
              ? "text-blue-600 dark:text-blue-400"
              : "text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300"
          }`}
        >
          <span className="flex items-center gap-2">
            <History className="size-4" />
            Attendance History
          </span>
          {activeTab === "history" && (
            <motion.div
              layoutId="tab-indicator"
              className="absolute bottom-0 left-0 right-0 h-0.5 bg-blue-600 dark:bg-blue-400 rounded-full"
            />
          )}
        </button>
      </div>

      {/* Tab content */}
      <AnimatePresence mode="wait">
        {activeTab === "live" ? (
          <LiveCaptureFeed
            key="live"
            events={liveEvents}
            isConnected={isConnected}
            isPaused={isPaused}
            onTogglePause={() => setIsPaused((p) => !p)}
            onClear={handleClear}
            totalSeen={totalSeen}
          />
        ) : (
          <HistoryTab
            key="history"
            events={historyEvents}
            total={historyTotal}
            page={historyPage}
            totalPages={historyTotalPages}
            isLoading={historyLoading}
            onPageChange={(p) => fetchHistory(p)}
          />
        )}
      </AnimatePresence>
    </motion.main>
  );
}
