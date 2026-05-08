"use client";

import { useState, useEffect, useRef } from "react";

const NUM_BRAZOS = 9;
const SERVOS_POR_BRAZO = 4;
const NOMBRES_SERVOS = ["Base", "Hombro", "Codo", "Muñeca"];

// Estado inicial: todos en 90°
const initAngles = () =>
  Array.from({ length: NUM_BRAZOS }, () =>
    Array.from({ length: SERVOS_POR_BRAZO }, () => 90)
  );

export default function PruebaServos() {
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<"idle" | "ok" | "error">("idle");
  const [statusMsg, setStatusMsg] = useState("");
  const [backendOk, setBackendOk] = useState<boolean | null>(null);
  const heartbeatRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Estado controlado de todos los sliders: angles[brazo][servo] = grados
  const [angles, setAngles] = useState<number[][]>(initAngles);

  // ── Heartbeat: solo verifica conexión, NO envía comandos de ángulo
  useEffect(() => {
    const ping = async () => {
      try {
        const r = await fetch("http://127.0.0.1:8000/servo/status");
        setBackendOk(r.ok);
      } catch {
        setBackendOk(false);
      }
    };
    ping();
    heartbeatRef.current = setInterval(ping, 3000);
    return () => { if (heartbeatRef.current) clearInterval(heartbeatRef.current); };
  }, []);

  const notify = (ok: boolean, msg: string) => {
    setStatus(ok ? "ok" : "error");
    setStatusMsg(msg);
    setTimeout(() => setStatus("idle"), 2000);
  };

  // Mueve todos los servos y sincroniza sliders
  const setAll = async (angle: number) => {
    setLoading(true);
    try {
      const r = await fetch(`http://127.0.0.1:8000/servo/test/all?angle=${angle}`, {
        method: "POST",
      });
      if (r.ok) {
        // Actualizar todos los sliders al mismo ángulo
        setAngles(Array.from({ length: NUM_BRAZOS }, () =>
          Array.from({ length: SERVOS_POR_BRAZO }, () => angle)
        ));
      }
      notify(r.ok, r.ok ? `Todos → ${angle}°` : `Error HTTP ${r.status}`);
    } catch (e) {
      notify(false, "Backend no responde");
      console.error(e);
    }
    setLoading(false);
  };

  // Mueve un servo individual y actualiza su slider
  const setOverride = async (arm_index: number, servo_index: number, angle: number) => {
    // Actualizar estado local inmediatamente (UI responsiva)
    setAngles(prev => {
      const next = prev.map(arm => [...arm]);
      next[arm_index][servo_index] = angle;
      return next;
    });
    try {
      const r = await fetch("http://127.0.0.1:8000/servo/test/override", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ arm_index, servo_index, angle }),
      });
      notify(r.ok,
        r.ok
          ? `Brazo ${arm_index + 1} · ${NOMBRES_SERVOS[servo_index]} → ${angle}°`
          : `Error HTTP ${r.status}`
      );
    } catch (e) {
      notify(false, "Backend no responde");
      console.error(e);
    }
  };

  return (
    <div className="p-8 min-h-screen bg-neutral-900 text-white font-sans">
      <h1 className="text-3xl font-bold mb-6 text-center text-blue-400">Prueba de Servos</h1>

      {/* Estado del backend */}
      <div className="flex justify-center mb-4">
        <span className={`px-4 py-1 rounded-full text-sm font-medium ${
          backendOk === null ? "bg-neutral-700 text-neutral-400" :
          backendOk ? "bg-green-800 text-green-300" : "bg-red-800 text-red-300"
        }`}>
          {backendOk === null ? "⏳ Conectando..." : backendOk ? "✅ Backend OK" : "❌ Backend no responde"}
        </span>
      </div>

      {/* Toast de feedback */}
      {status !== "idle" && (
        <div className={`fixed top-4 right-4 px-5 py-3 rounded-xl text-sm font-semibold shadow-lg z-50 ${
          status === "ok" ? "bg-green-700 text-white" : "bg-red-700 text-white"
        }`}>
          {statusMsg}
        </div>
      )}

      {/* Botones globales */}
      <div className="flex justify-center gap-4 mb-8">
        <button
          onClick={() => setAll(0)}
          className="bg-red-600 hover:bg-red-500 px-6 py-2 rounded-full font-semibold transition"
          disabled={loading}
        >
          Todos a 0°
        </button>
        <button
          onClick={() => setAll(90)}
          className="bg-blue-600 hover:bg-blue-500 px-6 py-2 rounded-full font-semibold transition"
          disabled={loading}
        >
          Todos a 90°
        </button>
        <button
          onClick={() => setAll(180)}
          className="bg-green-600 hover:bg-green-500 px-6 py-2 rounded-full font-semibold transition"
          disabled={loading}
        >
          Todos a 180°
        </button>
      </div>

      {/* Grid de brazos */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
        {Array.from({ length: NUM_BRAZOS }).map((_, armIdx) => (
          <div key={armIdx} className="bg-neutral-800 p-6 rounded-2xl shadow-xl border border-neutral-700">
            <h2 className="text-xl font-semibold mb-4 text-neutral-200">Brazo {armIdx + 1}</h2>

            <div className="space-y-4">
              {Array.from({ length: SERVOS_POR_BRAZO }).map((_, servoIdx) => (
                <div key={servoIdx}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-neutral-400">{NOMBRES_SERVOS[servoIdx]}</span>
                    <span className="text-blue-400 font-mono font-semibold">
                      {angles[armIdx][servoIdx]}°
                    </span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="180"
                    value={angles[armIdx][servoIdx]}
                    onChange={(e) => setOverride(armIdx, servoIdx, Number(e.target.value))}
                    className="w-full accent-blue-500"
                  />
                  <div className="flex justify-between text-xs text-neutral-600 mt-1">
                    <span>0°</span>
                    <span>180°</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
