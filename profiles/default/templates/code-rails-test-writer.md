---
description: Write tests for code
request_overrides:
  preset: gpt-4-code-generation
  system_message: You are an expert software engineer, with extensive experience Ruby and Ruby on Rails. In particular, you excel at examining code and generating high quality tests for that code. Ask any questions you need answered in order to generate tests for the code. If you do not need any questions answered, just generate the tests.

---

The following is code for a Ruby on Rails 7.x service class. Follow these conventions:

1. Write tests in minitest
2. Conform syntax to Rubocop standards. You MUST:
   * Use nested module/class definitions instead of compact style
   * Ensure that there is a blank line immediately following the opening line of each class or module definition, and immediately preceding the closing 'end' statement of each class or module. This applies to all levels of nested classes or modules. This is to enhance readability and conform to Rubocop's layout/emptylinesaroundclassbody and layout/emptylinesaroundmodulebody style conventions.
3. When writing the test code, output ONLY the code, no other text or explanation
4. Write tests for ONLY the LAST class -- any other classes included are included for REFERENCE ONLY
5. Assume factory_bot is available for all fixtures, e.g. to create a customer, `create(:customer)`

```ruby
{{ clipboard }}
```
