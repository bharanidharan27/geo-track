ALTER TABLE public.scan_events
ADD COLUMN IF NOT EXISTS facility_id STRING NULL;

ALTER TABLE public.scan_events
ADD COLUMN IF NOT EXISTS facility_type STRING NULL;

ALTER TABLE public.scan_events
ADD COLUMN IF NOT EXISTS sequence_no INT NULL;

ALTER TABLE public.scan_events
ADD COLUMN IF NOT EXISTS journey_stage STRING NULL;

ALTER TABLE public.scan_events
ADD COLUMN IF NOT EXISTS event_message STRING NULL;

ALTER TABLE public.scan_events
DROP CONSTRAINT IF EXISTS event_type_check;

ALTER TABLE public.scan_events
ADD CONSTRAINT event_type_check CHECK (
    event_type IN (
        'handoff',
        'arrival',
        'departure',
        'order_submitted',
        'label_created',
        'picked_up',
        'arrived_origin_hub',
        'departed_origin_hub',
        'in_transit',
        'arrived_destination_hub',
        'arrived_delivery_station',
        'out_for_delivery',
        'delivered',
        'delay',
        'exception',
        'failed_delivery',
        'rts'
    )
);

ALTER TABLE public.parcels
DROP CONSTRAINT IF EXISTS status_check;

ALTER TABLE public.parcels
ADD CONSTRAINT status_check CHECK (
    status IN (
        'created',
        'in_transit',
        'out_for_delivery',
        'delivered',
        'exception',
        'failed_delivery',
        'rts'
    )
);
