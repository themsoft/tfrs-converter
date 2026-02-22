import axios from 'axios';
import type {
  UploadResponse,
  MappingResponse,
  AdjustmentsResponse,
  BalanceSheetResponse,
  IncomeStatementResponse,
  ComparisonResponse,
} from '../types';
import { mockApi } from './mockData';

const USE_MOCK = false;

const client = axios.create({
  baseURL: '/api',
  timeout: 30000,
});

export const api = {
  upload: async (file: File): Promise<UploadResponse> => {
    if (USE_MOCK) return mockApi.upload(file);
    const formData = new FormData();
    formData.append('file', file);
    const { data } = await client.post<UploadResponse>('/upload', formData);
    return data;
  },

  getMapping: async (sessionId: string): Promise<MappingResponse> => {
    if (USE_MOCK) return mockApi.getMapping(sessionId);
    const { data } = await client.get<MappingResponse>(`/mapping/${sessionId}`);
    return data;
  },

  applyAdjustments: async (sessionId: string): Promise<AdjustmentsResponse> => {
    if (USE_MOCK) return mockApi.applyAdjustments(sessionId);
    const { data } = await client.post<AdjustmentsResponse>(`/adjustments/${sessionId}`, {});
    return data;
  },

  getAdjustments: async (sessionId: string): Promise<AdjustmentsResponse> => {
    if (USE_MOCK) return mockApi.getAdjustments(sessionId);
    const { data } = await client.get<AdjustmentsResponse>(`/reports/${sessionId}/adjustments`);
    return data;
  },

  getBalanceSheet: async (sessionId: string): Promise<BalanceSheetResponse> => {
    if (USE_MOCK) return mockApi.getBalanceSheet(sessionId);
    const { data } = await client.get<BalanceSheetResponse>(`/reports/${sessionId}/balance-sheet`);
    return data;
  },

  getIncomeStatement: async (sessionId: string): Promise<IncomeStatementResponse> => {
    if (USE_MOCK) return mockApi.getIncomeStatement(sessionId);
    const { data } = await client.get<IncomeStatementResponse>(`/reports/${sessionId}/income-statement`);
    return data;
  },

  getComparison: async (sessionId: string): Promise<ComparisonResponse> => {
    if (USE_MOCK) return mockApi.getComparison(sessionId);
    const { data } = await client.get<ComparisonResponse>(`/reports/${sessionId}/comparison`);
    return data;
  },
};
