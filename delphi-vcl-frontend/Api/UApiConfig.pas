unit UApiConfig;

interface

type
  TApiConfig = class
  private
    class var FBaseUrl: string;
    class function NormalizeBaseUrl(const AValue: string): string; static;
  public
    class function GetBaseUrl: string; static;
    class procedure SetBaseUrl(const AValue: string); static;
  end;

implementation

uses
  System.SysUtils,
  System.StrUtils;

class function TApiConfig.NormalizeBaseUrl(const AValue: string): string;
var
  LValue: string;
begin
  LValue := Trim(AValue);
  if LValue = '' then
    raise EArgumentException.Create('Base URL bos olamaz.');

  while EndsText('/', LValue) do
    Delete(LValue, Length(LValue), 1);

  Result := LValue;
end;

class function TApiConfig.GetBaseUrl: string;
begin
  Result := FBaseUrl;
end;

class procedure TApiConfig.SetBaseUrl(const AValue: string);
begin
  FBaseUrl := NormalizeBaseUrl(AValue);
end;

initialization
  TApiConfig.FBaseUrl := 'http://127.0.0.1:8000';

end.
