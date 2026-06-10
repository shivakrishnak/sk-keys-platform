#!/usr/bin/env ruby
# check_liquid_all.rb - Parse every .md file with Liquid and report all errors
# Usage: bundle exec ruby tmp/check_liquid_all.rb
require 'liquid'
require 'find'

errors = []
base   = File.expand_path('..', __dir__)
tm_dir = File.join(base, 'technical-mastery')

Find.find(tm_dir) do |path|
  next unless path.end_with?('.md')
  next if File.basename(path) == 'index.md'

  content = File.read(path, encoding: 'utf-8')
  # Strip YAML frontmatter before Liquid parse
  body = content.sub(/\A---\n.*?\n---\n/m, '')

  begin
    Liquid::Template.parse(body)
  rescue Liquid::SyntaxError => e
    rel = path.sub(base + '/', '').sub(base + '\\', '')
    errors << { file: rel, msg: e.message }
  rescue => e
    rel = path.sub(base + '/', '').sub(base + '\\', '')
    errors << { file: rel, msg: "#{e.class}: #{e.message}" }
  end
end

if errors.empty?
  puts "No Liquid errors found across #{Find.find(tm_dir).count { |p| p.end_with?('.md') }} files."
else
  puts "#{errors.size} Liquid error(s) found:\n\n"
  errors.each_with_index do |e, i|
    puts "#{i+1}. #{e[:file]}"
    puts "   #{e[:msg]}"
    puts
  end
end
