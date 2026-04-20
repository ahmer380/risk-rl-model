/*
This utility, written in C#, was used to generate the Blitz probability matrix CSV files in this folder. It computes battle outcome distributions from the Risk.Dice engine and writes matrix-style probability tables that are consumed by this project as precomputed data.

This source is adapted from the SMG Studio risk-dice codebase (https://github.com/smgstudio/risk-dice) and is kept here for provenance/documentation. It is not intended to run directly in this repository as-is, because the original Risk.Dice project dependencies and structure are not included in this forked context.
*/

using System;
using Risk.Dice;

internal class BlitzProbabilityMatrixGenerator
{
    static void Main(string[] args)
    {
        Console.WriteLine("=== RISK Dice Library Demo ===\n");
        generateBlitzProbabilityMatrixCsv(100);
        Console.WriteLine("\n=== All demos completed! ===");
    }

    static void generateBlitzProbabilityMatrixCsv(int dimension)
    {
        var outcomes = new List<(int, int)>(); //(remainingAttackers, remainingDefenders)
        for (int remainingAttackers = dimension; remainingAttackers >= 2; remainingAttackers--)
            outcomes.Add((remainingAttackers, 0));
        for (int remainingDefenders = 1; remainingDefenders <= dimension; remainingDefenders++)
            outcomes.Add((1, remainingDefenders));
        
        using (var writer = new System.IO.StreamWriter($"{dimension}_d_blitz_probability_matrix.csv"))
        {
            //Write header line
            writer.Write("Battle");
            foreach (var outcome in outcomes)
                writer.Write($",({outcome.Item1}/{outcome.Item2})");
            writer.Write(",Win");
            writer.WriteLine();

            // Write each battle row and their outcome probabilities
            for (int attackCount = dimension; attackCount >= 2; attackCount--)
            {
                for (int defendCount = dimension; defendCount >= 1; defendCount--)
                {
                    writer.Write($"({attackCount}/{defendCount})");

                    var battleConfig = new BattleConfig(attackCount - 1, defendCount, 0); //attackCount - 1 because the extra unit stays behind
                    var battle = BattleCache.Get(RoundConfig.Default, battleConfig);
                    battle.Calculate();

                    foreach (var outcome in outcomes)
                    {
                        string probability = "0.000";
                        
                        if (outcome.Item2 == 0) // Attacker wins
                        {
                            int attackLossCount = attackCount - outcome.Item1;
                            if (attackLossCount >= 0)
                                probability = battle.AttackLossChances[attackLossCount].ToString("F3");
                        }
                        else // Defender wins (outcome.Item1 == 1)
                        {
                            int defenderLossCount = defendCount - outcome.Item2;
                            if (defenderLossCount >= 0)
                                probability = battle.DefendLossChances[defenderLossCount].ToString("F3");
                        }

                        writer.Write($",{probability}");
                    }

                    writer.Write($",{battle.AttackWinChance:F3}");
                    writer.WriteLine();
                }
            }
        }

        Console.WriteLine($"Blitz probability matrix CSV generated: {dimension}_d_blitz_probability_matrix.csv");
    }

    static void computeBlitzBattleProbabilityDistribution(int attackCount, int defendCount)
    {
        Console.WriteLine($"Computing {attackCount} vs {defendCount} probability matrix for true random Blitz P(remainingAttackers, remainingDefenders)");
        
        var battleConfig = new BattleConfig(attackCount - 1, defendCount, 0); // attackCount - 1 because the extra unit stays behind
        var battle = BattleCache.Get(RoundConfig.Default, battleConfig);
        battle.Calculate();

        double sum = 0;
        for (int attackLossCount = 0; attackLossCount < battle.AttackLossChances.Length - 1; attackLossCount++) { //Attacker wins
            Console.WriteLine($"P({attackCount - attackLossCount}, 0) = {battle.AttackLossChances[attackLossCount]:F3}");
            sum += battle.AttackLossChances[attackLossCount];
        }

        for (int defenderLossCount = battle.DefendLossChances.Length - 2; defenderLossCount >= 0; defenderLossCount--) { //Defender wins
            Console.WriteLine($"P(1, {defendCount - defenderLossCount}) = {battle.DefendLossChances[defenderLossCount]:F3}");
            sum += battle.DefendLossChances[defenderLossCount];
        }

        Console.WriteLine($"Attacker win probability = {battle.AttackWinChance:F3}");
        Console.WriteLine($"Defender win probability = {battle.DefendWinChance:F3}");
    }
}
