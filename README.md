# dABI for TON Smart Contracts

The main goal is to allow developers to custom extend the dTON Index with their smart contracts and events.

dABI allows describing both states of smart contracts, results of get methods, and complex trace events with the
possibility of local debugging.

The final result is generated versioned using Github Actions and creates a new release.

## Documentation

Table of content:

1. SubTypes
    1. [Metdata]()
    2. [Labels]()
    3. [SmartContractSelector]()
    4. [TLB]()
    5. [TVM Types]()
2. Types
    1. [SmartContract]()
    2. [GetMethod]()
3. [Tests]()
4. [Json Generation]()

## Types

----

### Type: SmartContract

`get_methods` section allow you to define GetMethods. It can be imported from `schema/get_methods` with `get_method`
template keyword or defined in inline mode

`selector` section allow you to define which accounts will be parsed with such ABI

`state` section allow you to define how data of smart contract will be parsed

Each smart contract must have unique `label` with `name` on regex: `^[A-Za-z_][A-Za-z0-9_]*$`
Example ABI:

```yaml
apiVersion: dabi/v0
type: SmartContract
metadata:
  name: "My cool smart contract"
  description: "Completely not useless"
labels:
  name: my_contract
  dton_parse_prefix: parsed_smart_
spec:
  get_methods:
    - method_name: get_cool_smc
      result:
        - type: Int
          required: 0x100
    - {{ get_method("my_getter.yaml", indent=6) }}
  selector:
    by_methods: true
  state:
    tlb:
      inline: "message#3f5476ca value:# = SmartState;"
```

----

### Type: GetMethod

Each get method object MUST be linked to SmartContract to be parsed.<br/>
You can set several same (by `method_name`) GetMethods to one `SmartContract` instance.<br/>
Index system will automatically determinate which of `GetMethods` to use base on:

1. Result type check (if `result` present) and `result_strict_type_check` is `true` (default)
2. Number of result items if `result_length_strict_check` is `true` (default)
3. `required` value for `result` item (if presented any)

For type check dABI generates `type_hash` - sha256 of sorted (as result) JSON of types.

`method_args` / `method_result` uses as keys.

Example:

```json
{"method_args":[{"type":"Cell"},{"type":"Slice"},{"type":"Tuple","items":[{"type":"Int"}]}]}
```
Will have:

`1D11BE84A6C9FC477169F2E7E7D734C17CC6A096CAC6F34971D367D1E5209098` hash.

Type is same as described in `SubType` of [TVM Types]()

You can link one GetMethod object to several smart contracts with template system.

- `method_name` which defines smart contract GET method to call
- `args`* which describes input of GetMethod in `TVM Types`
- `result`* which describes output of GetMethod in `TVM Types`
- `result_strict_type_check`* - `true` by default, if `false` then index will parse only matching types
- `result_length_strict_check`* `true` by default, if `false` then index only min(abi_defined, smc_result) <br/>

(*) - optional

You can path GetMethod in inline mode or with template system.

Metadata and labels are copied to each method_name

To auto convert `Slice` / `Builder` / `Cell` to `Address` you can use:

```yaml
labels:
  address: true
```

This is better solution than add special type for TVM that doesn't exist. Also it much easier to hash check types
between ABI and TVM result.

For `Int` type `required` is int in hex or 10 base format.
For `Cell` / `Slice` / `Builder` `required` is hash of cell in HEX format

Each `type` has special auto created `label` with `name` key. It'll be `anon_X` if you don't define it directly. 
If you define it directly it MUST be in `^[A-Za-z_][A-Za-z0-9_]*$` regex pattern.

This special `name` label uses by [dton.co](https://dton.co) as column name in combine with `dton_parse_prefix`

Example ABI:

```yaml
apiVersion: dabi/v0
type: GetMethod
metadata:
  name: my-cool-get-method
  description: Get my cool data from this methods
labels:
  dton_parse_prefix: parsed_cool_
spec:
  - method_name: get_cool_smc
    args:
      - type: Cell
        metadata:
          name: Test cell
      - type: Slice
        tlb:
          file_path: "example.tlb"
          object: "SecondArg"
      - type: Tuple
        items:
          - type: Cell
            labels:
              name: my_cell
          - type: Slice
            tlb:
              file_path: "example.tlb"
              object: "SecondItem"
          - type: Tuple
            items:
              - type: Int
                name: important_int
    result:
      - type: Int
        required: 0x100
      - type: Cell
        metadata:
          name: Content of my NFT
        labels:
          field: content
  - method_name: second_method
    result:
      - type: Int
---

apiVersion: dabi/v0
type: GetMethod
...
```

---

## SubTypes

- Metadata - name / description / link of certain object
  ```yaml
  metadata:
    name: Example
    descripton: "My cool description"
    link: "https://example.com"
  ```
- Labels - custom extendable labels for index systems
  ```yaml
  labels:
    my_custom_label: "test"
  ```
- SmartContractSelector - rules for selecting accounts (smart contracts)<br/><br/>

  Apply ABI to smart contracts with specific group of GET methods:

  ```yaml
  selector:
    by_methods: true
  ```

  Apply ABI to smart contracts with certain code hash:

  ```yaml
  selector:
    by_code:
      - hash: "Hash of Cell in HEX"
      - hash: "Hash of Cell in base64"
        metadata:
          link: "https://github.com/..."
  ```

- TLB - types to match GetMethod result, smart contract state, messages<br/><br/>

  `file_path` - file path from root of `schema/tlb`<br/>
  `object` - name of TLB object<br/>
  `version`* - optional, basic version `tlb/v0` should work for you<br/>

  ```yaml
  tlb:
     version: tlb/v0
     file_path: ""
     object: ""
  ```

  Or `inline`:<br/>

  ```yaml
  tlb:
    inline: "message#3f5476ca value:# = CoolMessage;"
  ```

---

### TVM Types

1. Null
2. Int
3. Cell
4. Builder
5. Slice
6. Continuation
7. Tuple

## Tests

`smart_contract` defines information about smart contract to test
`cases` defines result answers.

For each case in `cases` you must provide `contract` file from `schema/contracts/` which will be tested.

```
apiVersion: dabi/v0
type: TestCase
smart_contract: 
  address: "..."
  block:
    workchain: -1
    shard: ...
    seqno: ...
    root_hash: ...
    file_hash: ...
cases:
  - contract: "contract.yaml"
    get_methods:
      - method_name: get_cool_smc
        result:
          - type: Int
            value: 1
          - type: Tuple
            value:
              - type: Int
                value: 2
              - type: Int
                value: 3
```

Testcases needed for auto-testing on different index systems.

## Json generation

## GetMethod type

All `metadata` / `labels` of GetMethod object merged to `metadata` / `label` of methods with priority to method.

Each method has `method_id` with crc32 value.

`result_strict_type_check` / `result_length_strict_check` always present.

For nested cases max depth is 1:

```yaml
apiVersion: dabi/v0
type: GetMethod
spec:
  - apiVersion: dabi/v0
    type: GetMethod
```

This is needed for template system. All such nested cases are flatten.

`method_result` / `method_args` are always present as lists.

`method_args_hash` / `method_result_hash` also automatically calculated and present in lists.

### TVM Type subtype

`required` for `Int` is always convert to 10 base.
`required` for Cell-like structures always uppercase hex.

`labels.name` always present and unique for each get method result including tuple items.

### TLB subtype

All TLB sources unify by unique uuid. In result json you will have `id` and `object` fields instead of TLB subtype.

All TLB sources defines in root of json in `tlb_soures` dict with `id's` keys and `{"version": "tlb/v0", "tlb": "..."}`
in value.

All TLB parsed and checked, also it's auto check that `object` presents in TLB source.

### Selector subtype

If selector by hash, all hashes have metadata ('' by default).
All hashes converted to uppercase hex.
It's guaranteed that for one context object (smart contract for example) there is one selector.

### Metadata subtype

Always has name, description, link as strings


---

By [dTON Tech team](https://tech.dton.co),
Based on [tongo ABI](https://github.com/tonkeeper/tongo/blob/master/abi/) and kubernetes helm charts.


