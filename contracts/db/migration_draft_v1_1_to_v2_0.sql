-- SafePassage Migration Draft: v1.1 -> v2.0
-- Target: PostgreSQL / Supabase
-- Purpose: align DB design with itinerary API shape (trip -> days -> locations/accommodation)
-- IMPORTANT: Review and test in staging first.

BEGIN;

-- =====================================================
-- 1) Additive schema changes (safe to apply first)
-- =====================================================

-- trips: ensure destination_country exists
ALTER TABLE IF EXISTS public.trips
  ADD COLUMN IF NOT EXISTS destination_country text;

-- new PREVENTION hierarchy
CREATE TABLE IF NOT EXISTS public.itinerary_days (
  id uuid PRIMARY KEY,
  trip_id uuid NOT NULL REFERENCES public.trips(id) ON DELETE CASCADE,
  day_id text,
  day_order integer NOT NULL,
  day_date date,
  label text,
  day_notes text,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.itinerary_locations (
  id uuid PRIMARY KEY,
  day_id uuid NOT NULL REFERENCES public.itinerary_days(id) ON DELETE CASCADE,
  location_id text,
  location_order integer NOT NULL,
  location_type text NOT NULL,
  name text,
  raw_text text,
  address_city text,
  address_state text,
  address_country text,
  geo_lat double precision,
  geo_lng double precision,
  geo_source text,
  start_local timestamptz,
  end_local timestamptz,
  timezone text,
  transport_mode text,
  transport_from_name text,
  transport_to_name text,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.itinerary_accommodations (
  id uuid PRIMARY KEY,
  day_id uuid NOT NULL UNIQUE REFERENCES public.itinerary_days(id) ON DELETE CASCADE,
  accom_id text,
  name text,
  raw_text text,
  address_line1 text,
  address_line2 text,
  address_city text,
  address_state text,
  address_country text,
  address_postal_code text,
  geo_lat double precision,
  geo_lng double precision,
  geo_source text,
  checkin_local timestamptz,
  checkout_local timestamptz,
  timezone text,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.itinerary_risk_queries (
  id uuid PRIMARY KEY,
  trip_id uuid NOT NULL REFERENCES public.trips(id) ON DELETE CASCADE,
  day_id uuid REFERENCES public.itinerary_days(id) ON DELETE CASCADE,
  location_ref_id uuid REFERENCES public.itinerary_locations(id) ON DELETE CASCADE,
  accommodation_ref_id uuid REFERENCES public.itinerary_accommodations(id) ON DELETE CASCADE,
  place_keywords jsonb NOT NULL DEFAULT '[]'::jsonb,
  country_code text,
  state text,
  district text,
  nearest_city text,
  lat double precision,
  lng double precision,
  is_overnight boolean NOT NULL DEFAULT false,
  created_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT chk_itinerary_risk_queries_ref
    CHECK (
      (location_ref_id IS NOT NULL AND accommodation_ref_id IS NULL)
      OR (location_ref_id IS NULL AND accommodation_ref_id IS NOT NULL)
    )
);

CREATE TABLE IF NOT EXISTS public.itinerary_risks (
  id uuid PRIMARY KEY,
  trip_id uuid NOT NULL REFERENCES public.trips(id) ON DELETE CASCADE,
  day_id uuid REFERENCES public.itinerary_days(id) ON DELETE CASCADE,
  location_ref_id uuid REFERENCES public.itinerary_locations(id) ON DELETE CASCADE,
  accommodation_ref_id uuid REFERENCES public.itinerary_accommodations(id) ON DELETE CASCADE,
  category text NOT NULL,
  risk_level text,
  recommendation text NOT NULL,
  source text,
  confidence numeric(5,2),
  connectivity_risk text,
  expected_offline_minutes integer CHECK (expected_offline_minutes >= 0),
  connectivity_confidence numeric(5,2),
  connectivity_notes text,
  created_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT chk_itinerary_risks_ref
    CHECK (
      (location_ref_id IS NOT NULL AND accommodation_ref_id IS NULL)
      OR (location_ref_id IS NULL AND accommodation_ref_id IS NOT NULL)
      OR (location_ref_id IS NULL AND accommodation_ref_id IS NULL)
    )
);

-- traveler_status alignment with new itinerary model
ALTER TABLE IF EXISTS public.traveler_status
  ADD COLUMN IF NOT EXISTS current_location_ref_id uuid;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM pg_constraint
    WHERE conname = 'traveler_status_current_location_ref_id_fkey'
  ) THEN
    ALTER TABLE public.traveler_status
      ADD CONSTRAINT traveler_status_current_location_ref_id_fkey
      FOREIGN KEY (current_location_ref_id)
      REFERENCES public.itinerary_locations(id)
      ON DELETE SET NULL;
  END IF;
END$$;

-- =====================================================
-- 2) Indexes for new model
-- =====================================================

CREATE INDEX IF NOT EXISTS idx_trips_destination_country
  ON public.trips(destination_country);

CREATE INDEX IF NOT EXISTS idx_itinerary_days_trip_order
  ON public.itinerary_days(trip_id, day_order);

CREATE INDEX IF NOT EXISTS idx_itinerary_locations_day_order
  ON public.itinerary_locations(day_id, location_order);

CREATE INDEX IF NOT EXISTS idx_itinerary_risk_queries_trip
  ON public.itinerary_risk_queries(trip_id, day_id);

CREATE INDEX IF NOT EXISTS idx_itinerary_risks_trip_category
  ON public.itinerary_risks(trip_id, category);

COMMIT;

-- =====================================================
-- 3) Optional cleanup (run ONLY after data migration)
-- =====================================================
-- BEGIN;
--
-- -- tables requested for removal
DROP TABLE IF EXISTS public.devices CASCADE;
DROP TABLE IF EXISTS public.alert_deliveries CASCADE;
DROP TABLE IF EXISTS public.phrase_packs CASCADE;

-- legacy PREVENTION tables replaced by itinerary_* design
DROP TABLE IF EXISTS public.itinerary_segments CASCADE;
DROP TABLE IF EXISTS public.risk_reports CASCADE;
DROP TABLE IF EXISTS public.connectivity_forecasts CASCADE;
DROP TABLE IF EXISTS public.risk_recommendations CASCADE;

-- optional: remove old traveler_status pointer after application switch-over
ALTER TABLE public.traveler_status
  DROP COLUMN IF EXISTS current_segment_id;

COMMIT;

-- =====================================================
-- 4) Optional compatibility view for old consumers
-- =====================================================
-- CREATE OR REPLACE VIEW public.v_legacy_itinerary_segments AS
-- SELECT
--   l.id,
--   d.trip_id,
--   l.location_order AS segment_order,
--   l.name AS segment_label,
--   l.transport_from_name AS start_place,
--   l.transport_to_name AS end_place,
--   r.expected_offline_minutes,
--   r.connectivity_risk,
--   EXTRACT(ISODOW FROM d.day_date)::int AS day_of_week,
--   l.start_local::time AS start_time_local,
--   l.end_local::time AS end_time_local,
--   l.created_at,
--   l.updated_at
-- FROM public.itinerary_locations l
-- JOIN public.itinerary_days d ON d.id = l.day_id
-- LEFT JOIN public.itinerary_risks r ON r.location_ref_id = l.id;
