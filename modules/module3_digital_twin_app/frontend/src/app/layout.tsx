import type { Metadata } from "next";
import "maplibre-gl/dist/maplibre-gl.css";

export const metadata: Metadata = {
  title: "SolarGIS Digital Twin Portal (60 FPS WebGL)",
  description: "Hệ thống Bản sao số & AI Đa luồng Giám sát Nhà máy Điện mặt trời (IEC TS 62446-3:2017)",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="vi">
      <body style={{ margin: 0, padding: 0, fontFamily: "system-ui, -apple-system, sans-serif", backgroundColor: "#0f172a", color: "#f8fafc" }}>
        {children}
      </body>
    </html>
  );
}
