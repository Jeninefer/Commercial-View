import axios from 'axios';
import { API_BASE_URL, API_TIMEOUT_MS } from './config';

const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT_MS,
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
});

export default client;
