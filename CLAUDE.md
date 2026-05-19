# CLAUDE.md

このファイルは、Claude Code (claude.ai/code) がこのリポジトリのコードを扱う際のガイダンスを提供する。

## プロジェクト概要

可逆プログラミング言語 Janus の Python インタプリタ（PyJanus）。現在の開発対象は `src/jana_py/` の Python インタプリタ。

## ビルド・実行

```bash
# インストール（編集可能モード、venv内）
make install          # または: python -m pip install -e src

# プログラムの実行
make run EXAMPLE=examples/fib.ja
PYTHONPATH=src python3 -m jana_py.cli examples/fib.ja

# オプション付き実行
PYTHONPATH=src python3 -m jana_py.cli -i examples/fib.ja    # 逆実行
PYTHONPATH=src python3 -m jana_py.cli -d examples/fib.ja    # デバッガ
PYTHONPATH=src python3 -m jana_py.cli -s examples/fib.ja    # 最終ストア表示
PYTHONPATH=src python3 -m jana_py.cli --std=janus1982 FILE     # 1982年厳格版
PYTHONPATH=src python3 -m jana_py.cli --std=janus1982ext FILE  # 1982風＋拡張
```

## テスト

```bash
make test             # 全テスト実行（src/tests/）
make smoke            # 高速サブセット: cstyle_syntax + basic_examples
make rc               # リリース候補リグレッション

# 単一テストファイル
PYTHONPATH=src python3 -m pytest src/tests/test_cstyle_syntax.py -q

# 単一テスト関数
PYTHONPATH=src python3 -m pytest src/tests/test_cstyle_syntax.py::test_name -q
```

## アーキテクチャ

**実行パイプライン:**
```
cli.py → preprocess.py → parser_*.py → validate.py → Runtime(program).run()
```

**4種のパーサ**（`--std` で選択）:
- `parser_janus2026.py` — デフォルト（`--std=janus2026`）、C風構文（`for`、`switch`、波括弧）
- `parser_jana2014.py` — `--std=jana2014`、モダンJana構文
- `parser_janus1982.py` — `--std=janus1982`、janus.pdf準拠の厳格版（int型のみ、パラメータなし手続き）
- `parser_janus1982ext.py` — `--std=janus1982ext`、1982風構文＋拡張（sized int、struct、local/delocal等）

**`src/jana_py/` の主要モジュール:**
- `ast.py` — ASTノード（frozen dataclass）
- `runtime.py` — 木走査インタプリタ、デバッガ、フレーム/セルモデル
- `inverse.py` / `invert.py` — プログラム反転（制御フローの逆転）
- `preprocess.py` — `#define`、`#include`、マクロ展開
- `c_codegen.py` — Cコード生成バックエンド
- `circuit.py` — 可逆回路合成
- `pebble.py` — 空間使用量プロファイリング（Bennett戦略）
- `format.py` — プリティプリンタ（AST → ソースコード）
- `encode.py` — 値のエンコード/デコード
- `bennett.py` — Bennett自動可逆化（compute-copy-uncompute）
- `equiv.py` — プログラム等価性チェッカ
- `errors.py` — エラー型定義

## 開発規約

- コンテキストを狭く保つ: `src/`、`tests/`、`examples/`、`docs/` に集中。
- 各変更は1テーマに限定。デバッガ・制御フロー・型・エラー処理を混在させない。
- まずスコープ限定のテストを実行し、それに通ってから全リグレッションを実行。
- 正常成功テストがリグレッションした場合、続行前に修正する。
- パリティの進捗は `docs/parity-backlog.md` で追跡。
- 文法仕様は `BNF.md`に記載。

## 言語機能（Janus）

可逆言語: すべての演算は可逆でなければならない。主な構成要素:
- **可逆代入:** `+=`、`-=`、`^=`（XOR）、`<=>`（スワップ）
- **制御フロー:** `if/fi`（入口/出口アサーション付き）、`from/do/loop/until` ループ
- **手続き:** `call`/`uncall`（順方向/逆方向呼び出し）
- **スコープ:** `local`/`delocal`、`ancilla`、`constant` ブロック
- **データ型:** 整数型（i8–i64、u8–u64）、bool、char、string、stack、struct、配列
- **入出力:** `printf`、`scanf`、`read`、`write`
- **スタック操作:** `push`/`pop`
