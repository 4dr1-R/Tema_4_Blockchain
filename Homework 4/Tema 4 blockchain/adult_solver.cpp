

#include <iostream>
#include <string>
#include <vector>
#include <thread>
#include <atomic>
#include <mutex>
#include <openssl/sha.h>

using namespace std;

const string ALPHABET =
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmn0123456789";

atomic<bool> found(false);
mutex output_mutex;
string answer;

unsigned char target[32];

bool check_hash(const string& s) {
    unsigned char digest[SHA256_DIGEST_LENGTH];

    SHA256(
        reinterpret_cast<const unsigned char*>(s.data()),
        s.size(),
        digest
    );

    for (int i = 0; i < 32; i++) {
        if (digest[i] != target[i])
            return false;
    }

    return true;
}

int hex_value(char c) {
    if (c >= '0' && c <= '9') return c - '0';
    if (c >= 'a' && c <= 'f') return c - 'a' + 10;
    if (c >= 'A' && c <= 'F') return c - 'A' + 10;
    return -1;
}

void worker(int thread_id, int num_threads) {
    int n = ALPHABET.size();

    for (int a = thread_id; a < n; a += num_threads) {
        for (int b = 0; b < n; b++) {
            if (a == b || found) continue;

            for (int c = 0; c < n; c++) {
                if (c == a || c == b || found) continue;

                for (int d = 0; d < n; d++) {
                    if (d == a || d == b || d == c || found)
                        continue;

                    for (int e = 0; e < n; e++) {
                        if (e == a || e == b ||
                            e == c || e == d || found)
                            continue;

                        string candidate = {
                            ALPHABET[a],
                            ALPHABET[b],
                            ALPHABET[c],
                            ALPHABET[d],
                            ALPHABET[e]
                        };

                        if (check_hash(candidate)) {
                            bool expected = false;

                            if (found.compare_exchange_strong(expected, true)) {
                                lock_guard<mutex> lock(output_mutex);
                                answer = candidate;
                            }

                            return;
                        }
                    }
                }
            }
        }
    }
}

int main(int argc, char* argv[]) {
    if (argc != 2) {
        cerr << "Usage: ./adult_solver HASH\n";
        return 1;
    }

    string hash = argv[1];

    if (hash.size() != 64) {
        cerr << "Invalid SHA256 hash\n";
        return 1;
    }

    for (int i = 0; i < 32; i++) {
        int hi = hex_value(hash[2*i]);
        int lo = hex_value(hash[2*i+1]);

        if (hi < 0 || lo < 0) return 1;

        target[i] = (hi << 4) | lo;
    }

    unsigned int threads = thread::hardware_concurrency();
    if (threads == 0) threads = 4;

    cout << "[*] Using " << threads << " threads\n";
    cout << "[*] Searching...\n";

    vector<thread> pool;

    for (unsigned int i = 0; i < threads; i++) {
        pool.emplace_back(worker, i, threads);
    }

    for (auto& t : pool)
        t.join();

    if (found) {
        cout << answer << endl;
        return 0;
    }

    cerr << "Not found\n";
    return 1;
}
