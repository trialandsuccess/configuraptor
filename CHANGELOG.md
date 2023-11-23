# Changelog

<!--next-version-placeholder-->

## v1.23.5 (2023-11-23)
### Fix
* **alias:** Alias not always detected (e.g. in the case of postponed) ([`041f82c`](https://github.com/trialandsuccess/configuraptor/commit/041f82c6750ef96c0fadf2fe7e803b0c9814d11b))

## v1.23.4 (2023-11-20)
### Fix
* **alias:** Freeze and set slots so it can be used in a dataclass ([`a382269`](https://github.com/trialandsuccess/configuraptor/commit/a38226932c67281667c34171e0b01a6fb98925c7))

## v1.23.3 (2023-11-20)
### Fix
* If alias points to an Optional key and it is missing, don't throw an error but set the value to None ([`26ec586`](https://github.com/trialandsuccess/configuraptor/commit/26ec5869d24a53f081a844d63ad4fe93ec0ebeb5))

## v1.23.2 (2023-11-15)
### Fix
* Require a reasonable modern version of typeguard ([`1f1cbee`](https://github.com/trialandsuccess/configuraptor/commit/1f1cbee121e0fb9a7a9576ab3e22d1d03ede0c11))

## v1.23.1 (2023-11-09)
### Fix
* **alias:** Work with postpone and update ([`3dc2ada`](https://github.com/trialandsuccess/configuraptor/commit/3dc2ada06ee3a14ead7f4861aab518c644716568))

## v1.23.0 (2023-11-09)
### Feature
* **alias:** You can now define aliases for keys ([`5c72993`](https://github.com/trialandsuccess/configuraptor/commit/5c72993a47af3f955d8f9c4275c22b13736c7456))

### Documentation
* **alias:** Added to example readme ([`72efe8f`](https://github.com/trialandsuccess/configuraptor/commit/72efe8fbe266c8903409036ac43adfcd6aa3112e))

## v1.22.3 (2023-11-09)
### Fix
* **postponed:** Sometimes the two objects are not the same, so use type check instead of identity check ([`af9c1bb`](https://github.com/trialandsuccess/configuraptor/commit/af9c1bb454ba7c89bd7a6fa873dd70b1c03dcf61))

## v1.22.2 (2023-11-09)
### Fix
* **env:** Default to converting types when loading from env ([`e939e48`](https://github.com/trialandsuccess/configuraptor/commit/e939e48f28892dfbbbc7b5dc312bcc50ad99bbe1))

## v1.22.1 (2023-11-09)
### Fix
* **.env:** Use cwd when looking for .env instead of package path ([`40df59d`](https://github.com/trialandsuccess/configuraptor/commit/40df59da1f693d3ace260f868d49ffe8aa60abd3))

## v1.22.0 (2023-11-09)
### Feature
* **update:** Improved updating via |= syntax and from env ([`b846ff4`](https://github.com/trialandsuccess/configuraptor/commit/b846ff4f62a65e0553aef3f921bbcc17de6caaaf))

## v1.21.0 (2023-11-07)
### Feature
* **env:** Cls.from_env function to load config from env (os.environ or dotenv) ([`1b16350`](https://github.com/trialandsuccess/configuraptor/commit/1b16350841de0abbaaf688c257db18208bcc18f3))

## v1.20.0 (2023-09-28)
### Feature
* **helpers:** Add as_binaryio helper ([`20e4f29`](https://github.com/trialandsuccess/configuraptor/commit/20e4f29b15ca5b867f685ee5cb1bc2c03da576b0))

## v1.19.1 (2023-09-26)


## v1.19.0 (2023-09-20)
### Feature
* **core:** Allow loading from a URL like you would a local file ([`aca52a9`](https://github.com/trialandsuccess/configuraptor/commit/aca52a9345e0d6ba969815208fa214a7525d6f6f))

### Documentation
* Explained usage of URLs in `load` in readme ([`cb265a4`](https://github.com/trialandsuccess/configuraptor/commit/cb265a4e841130ef6fc9602046570337fe7977ca))

## v1.18.2 (2023-09-20)
### Fix
* **mypy:** Load_into also accepts bytes so return value is fixed ([`db509f0`](https://github.com/trialandsuccess/configuraptor/commit/db509f07adc4e6f4cfca1f8eac702179fea5dc80))

## v1.18.1 (2023-09-20)
### Fix
* **asbytes:** Also expose from top-level lib + update examples ([`375ea47`](https://github.com/trialandsuccess/configuraptor/commit/375ea473059764c3b4b0c0397a865b5c74b12791))

## v1.18.0 (2023-09-20)
### Feature
* **binary:** Add asbytes() as shortcut for ._pack() ([`5caaa7d`](https://github.com/trialandsuccess/configuraptor/commit/5caaa7d9e68ed3cc4b0b2a0c3864d2ce7dd82e71))

## v1.17.3 (2023-09-18)
### Fix
* **binary:** Swapping out values with a different field now updates the container size ([`c76261a`](https://github.com/trialandsuccess/configuraptor/commit/c76261aa4daa6c1438cb1d62d59fc886e6667ed4))

## v1.17.2 (2023-09-18)
### Fix
* **binary:** Made ._pack work with split binary blocks ([`0393846`](https://github.com/trialandsuccess/configuraptor/commit/0393846b518f5340cc310ab3411c6d89834644aa))

### Documentation
* **binary:** Explained length is optional ([`65634f4`](https://github.com/trialandsuccess/configuraptor/commit/65634f42bbf530e5436a1444f3854616694cfe0b))

## v1.17.1 (2023-09-18)
### Fix
* **binary:** Allow splitting binary config into multiple blocks ([`f96adbb`](https://github.com/trialandsuccess/configuraptor/commit/f96adbb427aabce4d511fb838f89f9df0fb54d46))

## v1.17.0 (2023-09-18)
### Feature
* Allow a new type of config: binary config ([`06a70df`](https://github.com/trialandsuccess/configuraptor/commit/06a70df6e521deae2b0469621e5521c26a7dac88))

### Fix
* **binary:** .load should now also work with just a bytestring, no wrapping dict. ([`2f7f8fc`](https://github.com/trialandsuccess/configuraptor/commit/2f7f8fc86004f07e444e13f3d855cfce0b2926bb))

### Documentation
* Explained binary config in readme's ([`923b9e7`](https://github.com/trialandsuccess/configuraptor/commit/923b9e7e3a2bbb54bb66657ffce2551c8ce4aad9))

## v1.16.0 (2023-07-25)
### Feature
* A list of data can now also be loaded ([`e962cf8`](https://github.com/trialandsuccess/configuraptor/commit/e962cf8adf48ceff146ec495113c620c5879d777))

## v1.15.0 (2023-07-21)
### Feature
* Added 'fill' to TypedConfig class to update without overwrite ([`8e27361`](https://github.com/trialandsuccess/configuraptor/commit/8e2736124c675c5a0c7ffc648334158908d51f3b))

## v1.14.0 (2023-07-21)
### Feature
* Use empty data in `load` to read from pyproject.toml ([`6e48899`](https://github.com/trialandsuccess/configuraptor/commit/6e48899acb1908377f30bc731e6967dbe4cb7c28))

## v1.13.1 (2023-07-17)
### Fix
* If nested key is missing, don't crash but return empty data (and deal with error handling later) ([`822b671`](https://github.com/trialandsuccess/configuraptor/commit/822b67103a46245b1c4a958f1b809bbcf083f47f))

## v1.13.0 (2023-07-06)
### Feature
* Allow defining custom converters for `load_into(..., convert_types=True)` using `@configuraptor.converter` ([`2cf8c44`](https://github.com/trialandsuccess/configuraptor/commit/2cf8c44f6ecb41480f5bcc71385abbf668681ef1))
* Support custom File types using `@configuraptor.loader` ([`4d5ccb3`](https://github.com/trialandsuccess/configuraptor/commit/4d5ccb3868f4cae4c733dc12e134e28b0aee2d1a))

## v1.12.1 (2023-07-06)
### Documentation
* **readme:** Added info about .env and .ini ([`c6acc09`](https://github.com/trialandsuccess/configuraptor/commit/c6acc09391f9d5da1005aa64739032260d362c1c))

## v1.12.0 (2023-07-03)
### Feature
* Support .ini files and fix `convert_types` for recursion ([`9333029`](https://github.com/trialandsuccess/configuraptor/commit/9333029485eea936153320381181326ce862cfe6))

## v1.11.0 (2023-06-28)
### Feature
* **dotenv:** Support dotenv and add `lower_keys` and `convert_types` to `load_into` for dotenv ([`4d41197`](https://github.com/trialandsuccess/configuraptor/commit/4d41197a5d31cd623afb1f0ae61f720f27533a33))

## v1.10.0 (2023-06-26)
### Feature
* **init:** Allow ([args], {kwargs}) and [args] and {kwargs} for init! ([`0d19df8`](https://github.com/trialandsuccess/configuraptor/commit/0d19df8c47093fc35e9713672e2067c156cc7d47))

## v1.9.2 (2023-06-22)
### Fix
* Internal values (_) should be updatable without TypedConfig._update logic ([`ef24673`](https://github.com/trialandsuccess/configuraptor/commit/ef24673f4304fa58d2b51a429efe7dc62ddc84f9))

## v1.9.1 (2023-06-22)
### Fix
* Key="" workaround no longer required ([`2c5fcaf`](https://github.com/trialandsuccess/configuraptor/commit/2c5fcaf8471176b82ebf5438d677e8db657018ab))
* **mapping:** Made mapping immutable, so MutableMapping actually has different behavior ([`a68ef56`](https://github.com/trialandsuccess/configuraptor/commit/a68ef5651a457cc08f0125f01f00b98ceb49c544))

### Documentation
* **mapping:** Add example for TypedMapping ([`e430f40`](https://github.com/trialandsuccess/configuraptor/commit/e430f4065b5060fb2d2a4a8c134e8c42e9f66b74))

## v1.9.0 (2023-06-22)
### Feature
* **mapping:** Add configuraptor.TypedMapping and .TypedMutableMapping to support **unpacking (but not on default TypedConfig) ([`b4c6b9d`](https://github.com/trialandsuccess/configuraptor/commit/b4c6b9dc01cfd6727187310610e750fa6ada3234))

## v1.8.0 (2023-06-21)
### Feature
* **format:** Allow TypedConfig._format ([`0b46646`](https://github.com/trialandsuccess/configuraptor/commit/0b46646fec153a6bcdfea0c40b872da884aa9146))

## v1.7.2 (2023-06-20)
### Fix
* **toml:** Tomlkit had own types, move to tomli ([`0b5f0a4`](https://github.com/trialandsuccess/configuraptor/commit/0b5f0a4333f5767fc2329cebb040c6cf4c78eff9))

## v1.7.1 (2023-06-20)
### Fix
* **310:** Backwards compatible code ([`8f90aec`](https://github.com/trialandsuccess/configuraptor/commit/8f90aec43fd1fcd403f1b68d26e4d605ea346014))

## v1.7.0 (2023-06-20)


## v1.6.0 (2023-06-19)
### Feature
* **TypedConfig:** Added config.update ([`57a21c2`](https://github.com/trialandsuccess/configuraptor/commit/57a21c29cc12185dcc4a406eef3c77d9dbd056d5))

## v1.5.1 (2023-06-15)
### Fix
* **core:** Patch issue with `is_optional` ([`fd4a897`](https://github.com/trialandsuccess/configuraptor/commit/fd4a8972b847ac69eb012041188420a02880e696))

## v1.5.0 (2023-06-15)
### Feature
* **dumping:** Add methods to dump class instances to dict/toml/yaml/json ([`ea8232b`](https://github.com/trialandsuccess/configuraptor/commit/ea8232b6cf0d152520cbf11278851646eb1e96a9))

## v1.4.0 (2023-06-15)
### Feature
* **postpone:** Allow marking a field as `postponed` if you can't fill it in right away or from config (useful for cli tools with cli args) ([`1494000`](https://github.com/trialandsuccess/configuraptor/commit/1494000a0f373b83188f892c83e6c1bb5a7ae755))

## v1.3.2 (2023-06-15)
### Documentation
* **examples:** Added more examples ([`884d11a`](https://github.com/trialandsuccess/configuraptor/commit/884d11a3f77836de907772237f58e723e5b7995b))
* **examples:** Added more example code for the `basic` category ([`9782442`](https://github.com/trialandsuccess/configuraptor/commit/97824420e187d2ad01f597b4d458a55c535bb512))
* **examples:** Started on providing more examples ([`ca84ecb`](https://github.com/trialandsuccess/configuraptor/commit/ca84ecbbc755108a35dabb9f9395d78f68b13b11))

## v1.3.1 (2023-06-15)
### Fix
* **mypy:** `Type[C] | C` confused mypy so `load_into` (officially) only supports classes (not instances) now. ([`cd1c45e`](https://github.com/trialandsuccess/configuraptor/commit/cd1c45eae4c1fea0d7b9fa127a21655ae1c065b2))

## v1.3.0 (2023-06-14)
### Feature
* **strict:** Allow strict=False for load_into to ignore types (not recommended) ([`16853bb`](https://github.com/trialandsuccess/configuraptor/commit/16853bb62b88c229ca0d9487692f9688b504bcf2))

## v1.2.1 (2023-06-14)
### Fix
* **lib:** Exposed wrong method ([`d57b6df`](https://github.com/trialandsuccess/configuraptor/commit/d57b6df10e85693729ffb87f4ec36a7a932e1a3e))

## v1.2.0 (2023-06-14)
### Feature
* **lib:** Expose more methods externally + make second arg of all_annotations optional ([`63605ba`](https://github.com/trialandsuccess/configuraptor/commit/63605babb48ac2313e063def86608f82628688b7))

## v1.1.2 (2023-06-14)
### Fix
* **dataclass:** Support for default_factory ([`031c68d`](https://github.com/trialandsuccess/configuraptor/commit/031c68d676fd59529e41debc480235a29f206405))

### Documentation
* **readme:** Wrong package name oops ([`a9f7fad`](https://github.com/trialandsuccess/configuraptor/commit/a9f7fad7483dd55ff76655ec3a8feda9d55beef8))

## v1.1.1 (2023-06-14)
### Documentation
* **readme:** Change fixed image height to width for responsiveness ([`4ea3557`](https://github.com/trialandsuccess/configuraptor/commit/4ea3557e4cbb6eb2d3128a871209920f27e033ce))

## v1.1.0 (2023-06-14)
### Feature
* Added JSON and YAML file loading. ([`e4f920f`](https://github.com/trialandsuccess/configuraptor/commit/e4f920f0ab1ffaebea2b7b5ad64e33f54f034a33))

## v1.0.3 (2023-06-14)
### Fix
* **core:** Checking for a required parameterized type (e.g. list[str]) crashed for a missing key (with the wrong error) ([`68ccc1c`](https://github.com/trialandsuccess/configuraptor/commit/68ccc1c44e29c940d14acd6ce6b49e9885eaa03a))

### Documentation
* **readme:** Added first example code ([`da0b13d`](https://github.com/trialandsuccess/configuraptor/commit/da0b13d6e90fb0d26b1f33d804657a21304be745))
* **changelog:** Manually added changes ([`c1c40ef`](https://github.com/trialandsuccess/configuraptor/commit/c1c40efb568abec30578d38a0a92d97f398fc23b))
* **image:** Set height ([`78896b8`](https://github.com/trialandsuccess/configuraptor/commit/78896b8a53109c22e8c0875195dd486667a432f0))

## v1.0.2 (2023-06-14)
### Documentation
* set image size

### Build
* added `hatch` as dev dependency

## v1.0.1 (2023-06-14)
### Documentation
* Fix changelog and url in readme ([`59bc18b`](https://github.com/trialandsuccess/configuraptor/commit/59bc18ba5d968b5275253d1637d4f5ef3aa3182b))

## v1.0.0 (2023-06-14)
### BREAKING CHANGE
* renamed to 'configuraptor'

### Feature
* **py:** Trying to support python 3.10 ([`9f7b0f7`](https://github.com/trialandsuccess/configuraptor/commit/9f7b0f7b535e44ff95500aa677b3df60e2482bb7))

### Documentation
* **readme:** Fixed urls and extended sections ([`5fecc97`](https://github.com/trialandsuccess/configuraptor/commit/5fecc9728fb3ff1d09198003afbe37683aab6a5c))

## v0.1.0 (2023-06-13)
### Feature

* Work in progress, second beta version with 100% cov ([`37f4fb4`](https://github.com/robinvandernoord/typedconfig/commit/37f4fb4ad28bdaa1b1b78672656fb5558202d131))
* Work in progress, first working beta version without full docs etc. ([`cf90a93`](https://github.com/robinvandernoord/typedconfig/commit/cf90a93b43d293af1337e6156543673e6b540e2d))

### Fix

* **init:** One step closer to a more logical __init__ handling, just no args yet (only kwargs) ([`9274317`](https://github.com/robinvandernoord/typedconfig/commit/92743173885220f169762d298fa0c2692d0bfe04))

### Documentation

* **examples:** Todo: example about the singleton mixin ([`7b6b0c0`](https://github.com/robinvandernoord/typedconfig/commit/7b6b0c08d5900dd94817cbdc13b79c8bf2cf3a2d))

## v0.1.0 (2023-06-05)
### Feature

* Initial version of the demo plugin ([`dc02818`](https://github.com/robinvandernoord/su6-plugin-demo/commit/dc02818b5d361469fa0ca480eee7394628faad89))
