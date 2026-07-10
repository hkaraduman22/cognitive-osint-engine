unit UResultsService;

interface

uses
  System.SysUtils;

type
  EResultsServiceError = class(Exception);

  TCompanyResult = record
    Id: Integer;
    Name: string;
    Industry: string;
    City: string;
    ConfidenceScore: Integer;
    CreatedAt: string;
  end;

  TCompanyResults = TArray<TCompanyResult>;

  TResultsService = class
  public
    function GetCompanies(const AAramaId: Integer; const ABearerToken: string): TCompanyResults;
  end;

implementation

uses
  System.JSON,
  System.Net.HttpClient,
  UHttpApiClient;

function TResultsService.GetCompanies(const AAramaId: Integer; const ABearerToken: string): TCompanyResults;
var
  LClient: THttpApiClient;
  LResponse: IHTTPResponse;
  LJsonValue: TJSONValue;
  LJsonArray: TJSONArray;
  I: Integer;
  LItem: TJSONValue;
  LObj: TJSONObject;
  LCompany: TCompanyResult;
  function GetString(const AObject: TJSONObject; const AName: string): string;
  var
    LValue: TJSONValue;
  begin
    LValue := AObject.GetValue(AName);
    if Assigned(LValue) then
      Result := Trim(LValue.Value)
    else
      Result := '';
  end;

  function GetInt(const AObject: TJSONObject; const AName: string; const ADefault: Integer): Integer;
  var
    LValue: TJSONValue;
  begin
    LValue := AObject.GetValue(AName);
    if not Assigned(LValue) then
      Exit(ADefault);

    if LValue is TJSONNumber then
      Exit(TJSONNumber(LValue).AsInt);

    Result := StrToIntDef(Trim(LValue.Value), ADefault);
  end;
begin
  if AAramaId <= 0 then
    raise EResultsServiceError.Create('arama_id gecersiz.');

  if Trim(ABearerToken) = '' then
    raise EResultsServiceError.Create('JWT token bulunamadi.');

  LClient := THttpApiClient.Create;
  try
    LResponse := LClient.Get('/api/v1/companies?arama_id=' + IntToStr(AAramaId), ABearerToken);
    if (LResponse.StatusCode < 200) or (LResponse.StatusCode >= 300) then
      raise EResultsServiceError.CreateFmt('Results basarisiz. HTTP %d', [LResponse.StatusCode]);

    LJsonValue := TJSONObject.ParseJSONValue(LResponse.ContentAsString(TEncoding.UTF8));
    try
      if not (LJsonValue is TJSONArray) then
        raise EResultsServiceError.Create('Results yaniti dizi formatinda degil.');

      LJsonArray := TJSONArray(LJsonValue);
      SetLength(Result, LJsonArray.Count);

      for I := 0 to LJsonArray.Count - 1 do
      begin
        LItem := LJsonArray.Items[I];
        if not (LItem is TJSONObject) then
          raise EResultsServiceError.Create('Results kayit formati gecersiz.');

        LObj := TJSONObject(LItem);
        LCompany.Id := GetInt(LObj, 'id', 0);
        LCompany.Name := GetString(LObj, 'name');
        LCompany.Industry := GetString(LObj, 'industry');
        LCompany.City := GetString(LObj, 'city');
        LCompany.ConfidenceScore := GetInt(LObj, 'confidence_score', 0);
        LCompany.CreatedAt := GetString(LObj, 'created_at');

        Result[I] := LCompany;
      end;
    finally
      LJsonValue.Free;
    end;
  finally
    LClient.Free;
  end;
end;

end.
