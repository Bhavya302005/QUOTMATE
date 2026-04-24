import api, { getApiErrorMessage } from '../services/api';

export function useApi() {
  return {
    api,
    getApiErrorMessage,
  };
}
