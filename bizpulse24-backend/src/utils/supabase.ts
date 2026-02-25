import { createClient, SupabaseClient } from '@supabase/supabase-js';
import { config } from './config';

let supabaseClient: SupabaseClient | null = null;

export const getSupabaseClient = (): SupabaseClient => {
  if (!supabaseClient) {
    supabaseClient = createClient(config.supabase.url, config.supabase.anonKey);
  }
  return supabaseClient;
};

export const getSupabaseServiceClient = (): SupabaseClient => {
  return createClient(config.supabase.url, config.supabase.serviceRoleKey);
};
