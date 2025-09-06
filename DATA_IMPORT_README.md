# NBA Data Import Guide

This guide explains how to import your historical NBA data from CSV files into your Supabase database.

## 📁 Required CSV Files

Place these files in the `data/` directory:

1. **TeamHistories.csv** - Team information and history
2. **Players.csv** - Player biographical information
3. **Games.csv** - Game results and details
4. **TeamStatistics.csv** - Team-level statistics
5. **PlayerStatistics.csv** - Player-level statistics
6. **LeagueSchedule24_25.csv** - Current season schedule (optional)

## 🚀 Quick Start

### Step 1: Install Python Dependencies
```bash
python setup_python.py
```

### Step 2: Place CSV Files
Create a `data/` directory and place your CSV files there:
```
data/
├── TeamHistories.csv
├── Players.csv
├── Games.csv
├── TeamStatistics.csv
└── PlayerStatistics.csv
```

### Step 3: Run Import
```bash
python import_nba_data.py
```

## 📊 Import Process

The import process follows this order:

1. **Teams** - Import team information and create team mappings
2. **Players** - Import player data and create player mappings  
3. **Games** - Import historical game results
4. **Team Stats** - Import team-level statistics by season
5. **Player Stats** - Import player-level statistics by season

## 🔧 Configuration

### Environment Variables
Make sure your `.env` file has the correct database connection:
```env
DATABASE_URL="postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres"
```

### CSV File Format
The import scripts expect these column names in your CSV files:

#### TeamHistories.csv
- `TeamName` - Full team name
- Other columns are optional

#### Players.csv
- `PlayerName` - Full player name
- `Position` - Player position (PG, SG, SF, PF, C)
- `Height` - Player height (format: "6-8" or "6'8\"")
- `Weight` - Player weight in pounds
- `JerseyNumber` - Jersey number
- `Team` - Current team name

#### Games.csv
- `GameDate` - Game date (various formats supported)
- `HomeTeam` - Home team name
- `AwayTeam` - Away team name
- `HomeScore` - Home team score
- `AwayScore` - Away team score
- `SeasonType` - Regular Season, Playoffs, Preseason
- `Arena` - Arena name
- `Attendance` - Attendance number

#### TeamStatistics.csv
- `Team` - Team name
- `Season` - Season (e.g., "2023-24")
- `HomeScore` - Home team score
- `AwayScore` - Away team score
- `FieldGoalPercentage` - Field goal percentage
- `ThreePointPercentage` - Three-point percentage
- `FreeThrowPercentage` - Free throw percentage
- `Rebounds` - Rebounds
- `Assists` - Assists
- `Turnovers` - Turnovers
- `Steals` - Steals
- `Blocks` - Blocks

#### PlayerStatistics.csv
- `PlayerName` - Player name
- `Season` - Season (e.g., "2023-24")
- `Minutes` - Minutes played
- `Points` - Points scored
- `Rebounds` - Rebounds
- `Assists` - Assists
- `Steals` - Steals
- `Blocks` - Blocks
- `Turnovers` - Turnovers
- `FieldGoalPercentage` - Field goal percentage
- `ThreePointPercentage` - Three-point percentage
- `FreeThrowPercentage` - Free throw percentage

## 🛠️ Troubleshooting

### Common Issues

1. **Import fails with authentication error**
   - Check your `DATABASE_URL` in `.env`
   - Verify your Supabase project is active

2. **CSV file not found**
   - Make sure files are in the `data/` directory
   - Check file names match exactly

3. **Column not found errors**
   - Check your CSV column names match the expected format
   - Some columns are optional and will be skipped

4. **Memory issues with large files**
   - The import processes data in chunks
   - If you still have issues, consider splitting large CSV files

### Debug Mode

To see more detailed error messages, you can modify the import scripts to add more logging.

## 📈 Expected Results

After successful import, you should have:

- **Teams**: All NBA teams with conference/division information
- **Players**: All players with biographical data
- **Games**: Historical game results (10+ years)
- **Team Stats**: Season-level team statistics
- **Player Stats**: Season-level player statistics

## 🔄 Re-running Import

The import scripts are designed to be safe to run multiple times:
- Existing teams/players are skipped
- Duplicate games are not created
- Statistics are aggregated by season

## 📊 Verification

After import, you can verify the data:

```bash
# Test database connection
npm run db:test

# View data in Prisma Studio
npm run db:studio
```

## 🚀 Next Steps

Once your data is imported:

1. **Set up ML service** for predictions
2. **Build frontend dashboard** to view data
3. **Implement betting odds integration**
4. **Create prediction models**

## 📝 Notes

- The import process may take several minutes for large datasets
- Progress is shown during import
- Errors are logged but don't stop the entire process
- Some data cleaning and normalization is performed automatically
