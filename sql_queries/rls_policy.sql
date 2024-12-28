-- Enable RLS on the waitlist table
ALTER TABLE public.waitlist ENABLE ROW LEVEL SECURITY;

-- Create a policy that allows all operations for authenticated users
CREATE POLICY "Enable all access for authenticated users" ON public.waitlist
    FOR ALL
    TO authenticated
    USING (true)
    WITH CHECK (true);

-- Create a policy that allows insert for anonymous users
CREATE POLICY "Enable insert for anonymous users" ON public.waitlist
    FOR INSERT
    TO anon
    WITH CHECK (true);

-- Create a policy that allows select for anonymous users
CREATE POLICY "Enable select for anonymous users" ON public.waitlist
    FOR SELECT
    TO anon
    USING (true);
