import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.util.List;
import java.io.BufferedReader;
import java.io.FileReader;
import java.util.ArrayList;

class StringGenerator {

    public static List<String> generateStringsFromFile(String filePath) throws IOException {
        try (BufferedReader reader = new BufferedReader(new FileReader(filePath))) {
            List<String> lines = new ArrayList<>();
            String line;
            while ((line = reader.readLine()) != null) {
                if (!line.trim().isEmpty()) {
                    lines.add(line.trim());
                }
            }

            if (lines.isEmpty()) {
                throw new IllegalArgumentException("Empty file");
            }

            int currentLineIndex = 0;

            String s0 = lines.get(currentLineIndex++);
            if (currentLineIndex >= lines.size()) {
                throw new IllegalArgumentException("Missing argument");
            }

            String nextLine = lines.get(currentLineIndex);
            int j;
            try {
                Integer.parseInt(nextLine);
                j = 0;
                while (currentLineIndex + j < lines.size() && isInteger(lines.get(currentLineIndex + j))) {
                    j++;
                }
            } catch (NumberFormatException e) {
                j = 0;
            }

            String sj = generateIterativeString(s0, lines, currentLineIndex, j);
            currentLineIndex += j;

            if (currentLineIndex >= lines.size()) {
                return List.of(sj, "");
            }
            
            String t0 = lines.get(currentLineIndex++);
            
            int k = 0;
            while (currentLineIndex + k < lines.size() && isInteger(lines.get(currentLineIndex + k))) {
                k++;
            }
            
            String tk = generateIterativeString(t0, lines, currentLineIndex, k);
            currentLineIndex += k;

            return List.of(sj, tk);

        }
    }

    private static String generateIterativeString(String baseString, List<String> lines, int startIndex, int steps) {
        String currentString = baseString;
        
        for (int i = 0; i < steps; i++) {
            int stepIndex = startIndex + i;
            String indexLine = lines.get(stepIndex);
            int n;

            try {
                n = Integer.parseInt(indexLine);
            } catch (NumberFormatException e) {
                throw new IllegalArgumentException("Line " + (stepIndex + 1) + " is not valid integer");
            }

            if (n < 0 || n > currentString.length()) {
                throw new IllegalArgumentException("Index out of range at: " + (i + 1) + " the length of the string is " + currentString.length() + ", with index n = " + n + " out of range");
            }

            StringBuilder sb = new StringBuilder(currentString);
            
            String stringToInsert = currentString;
            
            sb.insert(n + 1, stringToInsert);
            
            currentString = sb.toString();
        }
        
        return currentString;
    }
    
    private static boolean isInteger(String s) {
        try {
            Integer.parseInt(s);
            return true;
        } catch (NumberFormatException e) {
            return false;
        }
    }
}

public class SequenceAligner {

    private static double getTimeInMilliseconds() { 
        return System.nanoTime()/1e6; 
    } 

    private static double getMemoryInKB() { 
        double total = Runtime.getRuntime().totalMemory(); 
        return (total-Runtime.getRuntime().freeMemory())/1e3; 
    } 

    private static final int GAP_COST = 30;

    private int getAlignmentCost(char c1, char c2) {
        // 1. Match
        if (c1 == c2) {
            return 0;
        }

        // 2. Mismatch
        switch (c1) {
            case 'A':
                if (c2 == 'C') return 110;
                if (c2 == 'G') return 48;
                if (c2 == 'T') return 94;
                break;
            case 'C':
                if (c2 == 'A') return 110;
                if (c2 == 'G') return 118;
                if (c2 == 'T') return 48;
                break;
            case 'G':
                if (c2 == 'A') return 48;
                if (c2 == 'C') return 118;
                if (c2 == 'T') return 110;
                break;
            case 'T':
                if (c2 == 'A') return 94;
                if (c2 == 'C') return 48;
                if (c2 == 'G') return 110;
                break;
        }

        System.err.println("Should only contain A, T, C, G.");
        System.exit(1);
        return Integer.MAX_VALUE / 2;
    }

    public void alignStringsAndWrite(String s1, String s2, String outputPath) {

        double beforeUsedMem = getMemoryInKB(); 
        double startTime = getTimeInMilliseconds(); 
        
        int m = s1.length();
        int n = s2.length();

        // 1. initialize dp table
        int[][] dp = new int[m + 1][n + 1];

        // 2. Base Cases
        
        for (int i = 0; i <= m; i++) {
            dp[i][0] = i * GAP_COST;
        }
        for (int j = 0; j <= n; j++) {
            dp[0][j] = j * GAP_COST;
        }

        // 3. fill in DP table
        for (int i = 1; i <= m; i++) {
            for (int j = 1; j <= n; j++) {
                
                char c1 = s1.charAt(i - 1); 
                char c2 = s2.charAt(j - 1); 

                // match or mismatch
                int matchMismatchCost = dp[i - 1][j - 1] + getAlignmentCost(c1, c2);

                // s1[i-1] matches a gap
                int gapInS2Cost = dp[i - 1][j] + GAP_COST;

                // s2[j-1] matches a gap
                int gapInS1Cost = dp[i][j - 1] + GAP_COST;

                dp[i][j] = Math.min(matchMismatchCost, Math.min(gapInS2Cost, gapInS1Cost));
            }
        }

        StringBuilder alignedS1 = new StringBuilder();
        StringBuilder alignedS2 = new StringBuilder();
        
        int i = m;
        int j = n;

        while (i > 0 || j > 0) {
            
            if (i > 0 && j > 0) {
                char c1 = s1.charAt(i - 1);
                char c2 = s2.charAt(j - 1);
                int expectedCost = dp[i - 1][j - 1] + getAlignmentCost(c1, c2);

                if (dp[i][j] == expectedCost) {
                    alignedS1.append(c1);
                    alignedS2.append(c2);
                    i--;
                    j--;
                    continue;
                }
            }

            if (i > 0 && dp[i][j] == dp[i - 1][j] + GAP_COST) {
                alignedS1.append(s1.charAt(i - 1));
                alignedS2.append('_');
                i--;
                continue;
            }
            
            if (j > 0) {
                alignedS1.append('_');
                alignedS2.append(s2.charAt(j - 1));
                j--;
            }
        }

        String finalS1 = alignedS1.reverse().toString();
        String finalS2 = alignedS2.reverse().toString();
        int finalCost = dp[m][n];

        double afterUsedMem = getMemoryInKB(); 
        double endTime = getTimeInMilliseconds(); 
 
        double totalUsage = afterUsedMem-beforeUsedMem; 
        double totalTime = endTime - startTime;

        try (BufferedWriter writer = new BufferedWriter(new FileWriter(outputPath))) {
            writer.write(String.valueOf(finalCost));
            writer.newLine();
            
            writer.write(finalS1);
            writer.newLine();

            writer.write(finalS2);
            writer.newLine();

            writer.write(Double.toString(totalTime));
            writer.newLine();

            writer.write(Double.toString(totalUsage));            
        } catch (IOException e) {
            System.err.println(e.getMessage());
            e.printStackTrace();
        }
    }

    public static void main(String[] args) throws IOException{
        String inputFilePath = args[0];
        String outputFilePath = args[1];

        List<String> inputStrs = StringGenerator.generateStringsFromFile(inputFilePath);

        SequenceAligner aligner = new SequenceAligner();

        // warm up starts
        for (int i = 0; i < 10; ++i) {
            List<String> warmUpStrs = StringGenerator.generateStringsFromFile("../Datapoints/in15.txt");
            aligner.alignStringsAndWrite(warmUpStrs.get(0), warmUpStrs.get(1), "WarmUp.txt");    
        }
        // warm up ends


        aligner.alignStringsAndWrite(inputStrs.get(0), inputStrs.get(1), outputFilePath);
    }
}