import Language.Haskell.TH (safe)
import Distribution.SPDX (LicenseId(NIST_PD_fallback))
-- fibonacci in O(n) time
-- n: how many numbers left to compute
-- import Data.Char (toUpper, toLower)

-- fib n = _fib n 0 1
--   where
--     _fib 0 a _ = a
--     _fib n a b = _fib (n-1) b (a+b)


-- addFive = (+ 5) -- same as addFive a = a + 5

-- f = (\g h i -> i h g) ["Carey"] [131]
-- -- input: function i with arguments h(["Chary"]) and g([131])
-- i h g = "h: " ++ show h ++ ", g: " ++ show g

-- swap f a b = f b a

-- cap_len :: [String] -> [(String, Int)]
-- cap_len ls = map (\(x:xs) -> (toUpper x : xs, length (x:xs))) ls

-- mashup s1 s2 n = take n s1 ++ reverse (take n s2)
-- mashup_curry = \s1 -> \s2 -> \n -> take n s1 ++ reverse (take n s2)
-- -- mashup_curry = (\s1 -> (\s2 -> (\n -> take n s1 ++ reverse (take n s2))))
-- -- in Python: mashup_curry = (lambda s1 : (lambda s2 : (lambda n : s1[:n] + s2[:n][::-1])))


-- data DLL =
--   Nil |
--   Node { prev :: DLL, value :: Int, next :: DLL}

-- fromList :: [Int] -> DLL
-- fromList [] = Nil
-- fromList (x:xs) = Node Nil x (fromList xs)

-- divis n m = [x | x <- [n..m], x `mod` 5 == 0 || x `mod` 7 == 0 || x `mod` 9 == 0]

-- countConsec [] _ = 1
-- countConsec a b
--   | length a > length b = 0
--   | take (length a) b == a = 1 + countConsec a (tail b)
--   | otherwise = countConsec a (tail b)

-- pytrips n = take n [(a, b, c) | c <- [1..], b <- [1..c], a <- [1..b], a^2 + b^2 == c^2]

-- unique_str s = [c | c <- s, count c s == 1]
--   where
--     count c s = length [x | x <- s, x == c]

substr sub s
  | length sub > length s = False
  | take (length sub) s == sub = True
  | otherwise = substr sub (tail s)

longest_run ls = fst (foldl (\(max_val, curr) x -> if x then ((max (curr+1) max_val), curr+1) else (max_val, 0)) (0, 0) ls)

main :: IO ()
main = do
  -- putStrLn (f i)
  -- print(cap_len ["cat", "mat", "baT_!"])
  -- print(unique_str "bannana")
  print (dup_rem (Node 1 (Node 1 (Node 2 (Node 3 (Node 3 Nil))))))
