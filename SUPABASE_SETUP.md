# Supabase Setup Guide for NBA Betting Prediction Model

## Step 1: Create Supabase Project

1. Go to [https://supabase.com](https://supabase.com)
2. Sign up/Login to your account
3. Click "New Project"
4. Choose your organization
5. Fill in project details:
   - **Name**: `nba-betting-prediction`
   - **Database Password**: Generate a strong password (save this!)
   - **Region**: Choose closest to your location
6. Click "Create new project"
7. Wait for the project to be created (2-3 minutes)

## Step 2: Get Connection Details

Once your project is ready:

1. Go to **Settings** → **Database**
2. Copy the following values:
   - **Host**: `db.[YOUR-PROJECT-REF].supabase.co`
   - **Database name**: `postgres`
   - **Port**: `5432`
   - **User**: `postgres`
   - **Password**: (the one you created)

3. Go to **Settings** → **API**
4. Copy these values:
   - **Project URL**: `https://[YOUR-PROJECT-REF].supabase.co`
   - **anon public key**: `eyJ...` (starts with eyJ)
   - **service_role key**: `eyJ...` (starts with eyJ)

## Step 3: Configure Environment Variables

Create a `.env.local` file in your project root with:

```env
# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=https://[YOUR-PROJECT-REF].supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here

# Database Configuration
DATABASE_URL="postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres?schema=public"

# NBA Data API (optional for now)
NBA_API_KEY=your_nba_api_key_here
```

## Step 4: Initialize Supabase in Your Project

Run these commands:

```bash
# Initialize Supabase in your project
npx supabase init

# Link to your remote project
npx supabase link --project-ref [YOUR-PROJECT-REF]

# Pull the remote schema (optional)
npx supabase db pull
```

## Step 5: Run Prisma Migrations

```bash
# Generate Prisma client
npx prisma generate

# Push schema to Supabase
npx prisma db push

# Or create a migration (recommended for production)
npx prisma migrate dev --name init
```

## Step 6: Verify Setup

1. Check your Supabase dashboard → **Table Editor**
2. You should see all the tables created:
   - teams
   - players
   - games
   - betting_odds
   - predictions
   - user_bets
   - team_stats
   - player_stats
   - model_performance

## Step 7: Test Connection

Create a simple test file to verify everything works:

```typescript
// test-connection.ts
import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

async function testConnection() {
  try {
    await prisma.$connect()
    console.log('✅ Database connection successful!')
    
    // Test a simple query
    const teamCount = await prisma.team.count()
    console.log(`📊 Teams in database: ${teamCount}`)
    
  } catch (error) {
    console.error('❌ Database connection failed:', error)
  } finally {
    await prisma.$disconnect()
  }
}

testConnection()
```

Run it with: `npx tsx test-connection.ts`

## Next Steps

Once setup is complete, you can:
1. Start populating with historical NBA data
2. Set up the ML service
3. Build the frontend dashboard
4. Implement real-time odds integration

## Troubleshooting

### Common Issues:

1. **Connection refused**: Check your DATABASE_URL format
2. **Authentication failed**: Verify your password and project ref
3. **Schema not found**: Make sure you're using the correct schema (public)
4. **Permission denied**: Check that your service role key has proper permissions

### Useful Commands:

```bash
# Check Prisma schema
npx prisma validate

# View database in Prisma Studio
npx prisma studio

# Reset database (careful!)
npx prisma migrate reset

# Check Supabase status
npx supabase status
```

## Database Schema Overview

Your database now includes:

- **Teams**: NBA team information with conference/division
- **Players**: Player details and team relationships
- **Games**: Historical game data with scores and metadata
- **BettingOdds**: Historical and current betting lines
- **Predictions**: ML model predictions with confidence scores
- **UserBets**: User betting history and performance tracking
- **TeamStats**: Team performance statistics by season
- **PlayerStats**: Player performance statistics
- **ModelPerformance**: ML model accuracy and ROI tracking

This schema supports:
- ✅ 10+ years of historical data
- ✅ Real-time odds integration
- ✅ ML prediction tracking
- ✅ User betting performance
- ✅ Comprehensive analytics
