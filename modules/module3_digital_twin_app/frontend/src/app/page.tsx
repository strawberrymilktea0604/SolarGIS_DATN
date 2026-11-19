"use client";

import React, { useEffect, useRef, useState } from "react";
import maplibregl from "maplibre-gl";

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8080";

interface SelectedModuleInfo {
  mvt_id: number;
  module_id: string;
  row_id: number;
  pin_index: number;
  current_health_status: string;
  current_coa_class: number;
  is_distorted_recovered: boolean;
}

export default function SolarDigitalTwinPortal() {
  const mapContainerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);

  const [plantId, setPlantId] = useState<number>(1);
  const [activeFilter, setActiveFilter] = useState<"ALL" | "COA2" | "COA3">("ALL");
  const [selectedModule, setSelectedModule] = useState<SelectedModuleInfo | null>(null);
  const [backendStatus, setBackendStatus] = useState<string>("Đang kiểm tra...");

  useEffect(() => {
    fetch(`${BACKEND_URL}/api/health`)
      .then((r) => r.json())
      .then((d) => setBackendStatus(d.postgis_connected ? "Đã kết nối PostGIS & Rust Axum" : "Chưa kết nối PostGIS"))
      .catch(() => setBackendStatus("Backend Rust Axum chưa bật (Port 8080)"));
  }, []);

  useEffect(() => {
    if (!mapContainerRef.current || mapRef.current) return;

    // Tọa độ mặc định vùng lưới Thuận Nam 19 (EPSG:32649 -> WGS84 ~ 108.888 E, 11.438 N)
    const map = new maplibregl.Map({
      container: mapContainerRef.current,
      style: {
        version: 8,
        sources: {
          "osm-dark": {
            type: "raster",
            tiles: ["https://basemaps.cartocdn.com/dark_all/{z}/{x}/{y}@2x.png"],
            tileSize: 256,
            attribution: "&copy; OpenStreetMap &copy; CARTO",
          },
          solar_modules: {
            type: "vector",
            tiles: [`${BACKEND_URL}/api/tiles/${plantId}/{z}/{x}/{y}.mvt`],
            minzoom: 14,
            maxzoom: 22,
          },
        },
        layers: [
          {
            id: "background-map",
            type: "raster",
            source: "osm-dark",
          },
          {
            id: "solar-modules-fill",
            type: "fill",
            source: "solar_modules",
            "source-layer": "solar_modules_layer",
            paint: {
              // Chuẩn DATA_CONTRACT.md Mục 6.2:
              // Ưu tiên đọc feature-state (coa_class), fallback về current_coa_class của đợt bay mới nhất
              "fill-color": [
                "match",
                ["coalesce", ["feature-state", "coa_class"], ["get", "current_coa_class"]],
                3,
                "#ef4444", // CoA 3 - Đỏ (Safety-relevant abnormality)
                2,
                "#f59e0b", // CoA 2 - Vàng cam (Thermal abnormality)
                "#22c55e", // CoA 1 - Xanh lá (Normal)
              ],
              "fill-opacity": 0.78,
            },
          },
          {
            id: "solar-modules-outline",
            type: "line",
            source: "solar_modules",
            "source-layer": "solar_modules_layer",
            paint: {
              "line-color": "#0f172a",
              "line-width": 0.8,
            },
          },
        ],
      },
      center: [108.893, 11.439],
      zoom: 17.2,
      maxZoom: 22,
    });

    map.addControl(new maplibregl.NavigationControl(), "top-right");

    map.on("click", "solar-modules-fill", (e) => {
      if (!e.features || e.features.length === 0) return;
      const feat = e.features[0];
      const props = feat.properties || {};
      setSelectedModule({
        mvt_id: Number(feat.id ?? props.mvt_id_prop ?? 0),
        module_id: String(props.module_id ?? ""),
        row_id: Number(props.row_id ?? 1),
        pin_index: Number(props.pin_index ?? 1),
        current_health_status: String(props.current_health_status ?? "NORMAL"),
        current_coa_class: Number(props.current_coa_class ?? 1),
        is_distorted_recovered: Boolean(props.is_distorted_recovered),
      });
    });

    map.on("mouseenter", "solar-modules-fill", () => {
      map.getCanvas().style.cursor = "pointer";
    });
    map.on("mouseleave", "solar-modules-fill", () => {
      map.getCanvas().style.cursor = "";
    });

    mapRef.current = map;

    return () => {
      map.remove();
      mapRef.current = null;
    };
  }, [plantId]);

  const handleFilterChange = (filter: "ALL" | "COA2" | "COA3") => {
    setActiveFilter(filter);
    const map = mapRef.current;
    if (!map) return;

    if (filter === "ALL") {
      map.setFilter("solar-modules-fill", null);
    } else if (filter === "COA2") {
      map.setFilter("solar-modules-fill", ["==", ["get", "current_coa_class"], 2]);
    } else if (filter === "COA3") {
      map.setFilter("solar-modules-fill", ["==", ["get", "current_coa_class"], 3]);
    }
  };

  return (
    <div style={{ display: "flex", height: "100vh", width: "100vw", overflow: "hidden" }}>
      {/* Sidebar Điều khiển & Inspector Drawer */}
      <aside
        style={{
          width: "360px",
          backgroundColor: "#1e293b",
          borderRight: "1px solid #334155",
          padding: "20px",
          display: "flex",
          flexDirection: "column",
          gap: "16px",
          overflowY: "auto",
        }}
      >
        <div>
          <h1 style={{ fontSize: "18px", fontWeight: 700, margin: "0 0 4px 0", color: "#38bdf8" }}>
            SOLARGIS DIGITAL TWIN
          </h1>
          <p style={{ fontSize: "12px", color: "#94a3b8", margin: 0 }}>
            Rust Axum + PostGIS ST_AsMVT + MapLibre WebGL 60 FPS
          </p>
        </div>

        <div style={{ padding: "10px 12px", borderRadius: "6px", backgroundColor: "#0f172a", fontSize: "12.5px" }}>
          <strong>Trạng thái Backend:</strong>{" "}
          <span style={{ color: backendStatus.includes("Đã kết nối") ? "#4ade80" : "#fbbf24" }}>
            {backendStatus}
          </span>
        </div>

        {/* Bộ chọn trang trại */}
        <div>
          <label style={{ fontSize: "12.5px", fontWeight: 600, display: "block", marginBottom: "6px" }}>
            Chọn Nhà máy Điện mặt trời (4 Trang trại):
          </label>
          <select
            value={plantId}
            onChange={(e) => setPlantId(Number(e.target.value))}
            style={{
              width: "100%",
              padding: "8px 10px",
              borderRadius: "6px",
              backgroundColor: "#0f172a",
              color: "#f8fafc",
              border: "1px solid #475569",
            }}
          >
            <option value={1}>1. Thuận Nam 19 (36.544 tấm pin - TN19)</option>
            <option value={2}>2. Nhà máy BIM 2 (BIM2)</option>
            <option value={3}>3. Thuận Nam Đức Long (TNDL)</option>
            <option value={4}>4. Điện mặt trời Thiên Tân 1.2 (TT12)</option>
          </select>
        </div>

        {/* Bộ lọc Phân hạng Bất thường Nhiệt IEC TS 62446-3 */}
        <div>
          <label style={{ fontSize: "12.5px", fontWeight: 600, display: "block", marginBottom: "6px" }}>
            Bộ lọc Chuẩn IEC TS 62446-3 (Classes of Abnormality):
          </label>
          <div style={{ display: "flex", gap: "6px" }}>
            {(["ALL", "COA2", "COA3"] as const).map((f) => (
              <button
                key={f}
                onClick={() => handleFilterChange(f)}
                style={{
                  flex: 1,
                  padding: "7px 8px",
                  borderRadius: "6px",
                  border: "1px solid #475569",
                  cursor: "pointer",
                  fontSize: "12px",
                  fontWeight: 600,
                  backgroundColor: activeFilter === f ? "#0284c7" : "#0f172a",
                  color: "#f8fafc",
                }}
              >
                {f === "ALL" ? "Tất cả" : f === "COA2" ? "CoA 2 (Vàng)" : "CoA 3 (Đỏ)"}
              </button>
            ))}
          </div>
        </div>

        {/* Chú giải Màu sắc */}
        <div style={{ padding: "12px", borderRadius: "6px", backgroundColor: "#0f172a", fontSize: "12.5px" }}>
          <div style={{ fontWeight: 600, marginBottom: "8px" }}>Chú giải Phân hạng IEC TS 62446-3:</div>
          <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "4px" }}>
            <span style={{ width: 12, height: 12, borderRadius: 3, backgroundColor: "#22c55e", display: "inline-block" }} />
            <span>CoA 1: Khỏe mạnh (Normal / OK)</span>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "4px" }}>
            <span style={{ width: 12, height: 12, borderRadius: 3, backgroundColor: "#f59e0b", display: "inline-block" }} />
            <span>CoA 2: Bất thường nhiệt (Theo dõi O&M)</span>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <span style={{ width: 12, height: 12, borderRadius: 3, backgroundColor: "#ef4444", display: "inline-block" }} />
            <span>CoA 3: Nguy cơ mất an toàn (Can thiệp sớm)</span>
          </div>
        </div>

        {/* Inspector Drawer khi Click vào 1 tấm pin */}
        <div
          style={{
            padding: "14px",
            borderRadius: "8px",
            backgroundColor: "#0f172a",
            border: "1px solid #334155",
            flex: 1,
          }}
        >
          <div style={{ fontWeight: 700, fontSize: "13.5px", marginBottom: "10px", color: "#38bdf8" }}>
            Chi tiết Tấm pin (Inspector Drawer)
          </div>
          {selectedModule ? (
            <div style={{ fontSize: "13px", lineHeight: 1.7 }}>
              <div>
                <strong>Mã định danh (`module_id`):</strong>
                <div style={{ color: "#4ade80", fontFamily: "monospace", fontSize: "13px" }}>
                  {selectedModule.module_id}
                </div>
              </div>
              <div>
                <strong>Khóa nguyên Vector Tile (`mvt_id`):</strong> <code>{selectedModule.mvt_id}</code>
              </div>
              <div>
                <strong>Hàng (`Row_ID`) / Thứ tự (`ID_Pin`):</strong> Hàng {selectedModule.row_id} — Tấm #{selectedModule.pin_index}
              </div>
              <div>
                <strong>Trạng thái sức khỏe:</strong> <code>{selectedModule.current_health_status}</code>
              </div>
              <div>
                <strong>Phân hạng IEC 62446-3:</strong>{" "}
                <span
                  style={{
                    padding: "2px 6px",
                    borderRadius: "4px",
                    backgroundColor:
                      selectedModule.current_coa_class === 3
                        ? "#ef4444"
                        : selectedModule.current_coa_class === 2
                        ? "#f59e0b"
                        : "#22c55e",
                    color: "#0f172a",
                    fontWeight: 700,
                  }}
                >
                  CoA {selectedModule.current_coa_class}
                </span>
              </div>
              <div>
                <strong>Khôi phục vùng méo Ortho:</strong>{" "}
                {selectedModule.is_distorted_recovered ? "Có (AI 1 + Snapping)" : "Không (Lưới chuẩn)"}
              </div>
            </div>
          ) : (
            <p style={{ fontSize: "12.5px", color: "#94a3b8", margin: 0 }}>
              Bấm trực tiếp vào bất kỳ tấm pin nào trên bản đồ WebGL bên phải để xem mã <code>module_id</code>, khóa <code>mvt_id</code> và trạng thái nhiệt chuẩn IEC TS 62446-3.
            </p>
          )}
        </div>
      </aside>

      {/* Khung Bản đồ MapLibre GL JS 60 FPS */}
      <main style={{ flex: 1, position: "relative" }}>
        <div ref={mapContainerRef} style={{ width: "100%", height: "100%" }} />
      </main>
    </div>
  );
}
