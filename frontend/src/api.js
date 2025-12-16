import axios from "axios";

// Railway 배포에서 VITE_API_BASE_URL이 누락되면 기본값으로 백엔드 도메인을 사용
// (로컬 개발 시에는 .env에 VITE_API_BASE_URL=http://127.0.0.1:8000 등을 넣으면 됨)
const DEFAULT_API_BASE_URL = "https://musicscope-production.up.railway.app";

const rawBaseUrl = import.meta.env.VITE_API_BASE_URL || DEFAULT_API_BASE_URL;
// trailing slash 정리 (https://.../ -> https://...)
const baseURL = rawBaseUrl.replace(/\/+$/, "");

export const api = axios.create({
  baseURL,
  timeout: 20000,
  withCredentials: false,
});